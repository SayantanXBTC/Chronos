"""Schema linter for historical entity data files.

Run:
    python -m data validate data/raw/political/east-asia/han-dynasty/phase-1.geojson
    python -m data validate --all
    python -m data validate --place-names
"""
from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from shapely.geometry import shape

from .constants import VALID_ENTITY_TYPES

HEX_COLOR_RE = re.compile(r'^#[0-9A-Fa-f]{6}$')
VALID_CONFIDENCE_TYPES = {'exact', 'approximate', 'inferred', 'disputed'}
VALID_DATE_PRECISIONS = {'exact', 'approximate', 'estimated'}

# Path to the entities YAML directory (sibling of this module)
_ENTITIES_DIR = Path(__file__).parent / 'entities'


@dataclass
class ValidationResult:
    path: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def _load_yaml_config(slug: str) -> dict[str, Any] | None:
    """Load entity YAML config by slug. Returns None if not found."""
    yaml_path = _ENTITIES_DIR / f'{slug}.yml'
    if not yaml_path.exists():
        return None
    with yaml_path.open('r', encoding='utf-8') as fh:
        return yaml.safe_load(fh)


def _check_coordinates(coords, result: ValidationResult, feature_idx: int, depth: int = 0) -> None:
    """Recursively check coordinate bounds for a coordinate array."""
    if not coords:
        return
    # Check if this is a list of numbers (a coordinate pair/triplet)
    if isinstance(coords[0], (int, float)):
        lon = coords[0]
        lat = coords[1]
        if not (-180 <= lon <= 180):
            result.errors.append(
                f"Feature {feature_idx}: coordinate lon={lon} out of WGS84 bounds [-180, 180]"
            )
        if not (-90 <= lat <= 90):
            result.errors.append(
                f"Feature {feature_idx}: coordinate lat={lat} out of WGS84 bounds [-90, 90]"
            )
    else:
        for sub in coords:
            _check_coordinates(sub, result, feature_idx, depth + 1)


def validate_geojson_file(path: Path | str) -> ValidationResult:
    """Validate a single GeoJSON phase file. Returns errors + warnings."""
    path = Path(path)
    result = ValidationResult(path=str(path))

    # Load GeoJSON
    try:
        with path.open('r', encoding='utf-8') as fh:
            data = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        result.errors.append(f"Cannot read/parse GeoJSON: {exc}")
        return result

    # Determine slug from parent directory name
    slug = path.parent.name

    # Load sibling YAML config for color check (check 3)
    yaml_config = _load_yaml_config(slug)

    # Check 3: color in YAML config
    if yaml_config is not None:
        color = yaml_config.get('color')
        if color is not None:
            if not HEX_COLOR_RE.match(str(color)):
                result.errors.append(
                    f"YAML config for '{slug}': color '{color}' is not a valid hex color (#RRGGBB)"
                )
        # else: color missing from YAML is not an error here

    # Handle both Feature and FeatureCollection
    if data.get('type') == 'Feature':
        features = [data]
    elif data.get('type') == 'FeatureCollection':
        features = data.get('features', [])
    else:
        result.errors.append(f"Top-level GeoJSON type must be 'Feature' or 'FeatureCollection', got: {data.get('type')!r}")
        return result

    for idx, feature in enumerate(features):
        props = feature.get('properties') or {}
        geometry = feature.get('geometry')

        # Check 1: source_license non-null for external sources — warn if missing
        source_license = props.get('source_license')
        if source_license is None:
            result.warnings.append(
                f"Feature {idx}: 'source_license' is missing (hand-traced files may omit)"
            )

        # Check 2: year_start < year_end when year_end is not null
        year_start = props.get('year_start')
        year_end = props.get('year_end')
        if year_start is not None and year_end is not None:
            try:
                if int(year_start) >= int(year_end):
                    result.errors.append(
                        f"Feature {idx}: year_start ({year_start}) must be < year_end ({year_end})"
                    )
            except (TypeError, ValueError):
                result.errors.append(
                    f"Feature {idx}: year_start/year_end must be numeric, got {year_start!r}/{year_end!r}"
                )

        # Check 4: importance in [1, 10] when present
        importance = props.get('importance')
        if importance is not None:
            try:
                imp_val = float(importance)
                if not (1 <= imp_val <= 10):
                    result.errors.append(
                        f"Feature {idx}: importance={importance} is out of range [1, 10]"
                    )
            except (TypeError, ValueError):
                result.errors.append(
                    f"Feature {idx}: importance must be numeric, got {importance!r}"
                )

        # Check 5: confidence_type in valid set when present
        confidence_type = props.get('confidence_type')
        if confidence_type is not None:
            if confidence_type not in VALID_CONFIDENCE_TYPES:
                result.errors.append(
                    f"Feature {idx}: confidence_type={confidence_type!r} not in "
                    f"{sorted(VALID_CONFIDENCE_TYPES)}"
                )

        # Check 6: date_precision in valid set when present
        date_precision = props.get('date_precision')
        if date_precision is not None:
            if date_precision not in VALID_DATE_PRECISIONS:
                result.errors.append(
                    f"Feature {idx}: date_precision={date_precision!r} not in "
                    f"{sorted(VALID_DATE_PRECISIONS)}"
                )

        # Check 7: WGS84 bounds
        if geometry and geometry.get('coordinates') is not None:
            _check_coordinates(geometry['coordinates'], result, idx)

        # Check 8: No self-intersecting rings (Shapely is_valid)
        if geometry:
            try:
                shp = shape(geometry)
                if not shp.is_valid:
                    import shapely as _shapely
                    reason = _shapely.is_valid_reason(shp)
                    result.errors.append(
                        f"Feature {idx}: geometry is invalid (self-intersecting or degenerate): "
                        f"{reason}"
                    )
            except Exception as exc:
                result.errors.append(
                    f"Feature {idx}: could not parse geometry with Shapely: {exc}"
                )

    return result


def validate_place_names_csv(path: Path | str) -> ValidationResult:
    """Validate ancient_cities.csv for duplicates, bounds, ranges."""
    path = Path(path)
    result = ValidationResult(path=str(path))

    try:
        with path.open('r', encoding='utf-8', newline='') as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
    except OSError as exc:
        result.errors.append(f"Cannot read CSV: {exc}")
        return result

    # Collect records for duplicate check (check 9)
    # Group by (lon, lat, name) and check for overlapping time ranges
    from collections import defaultdict
    groups: dict[tuple, list[tuple[int, Any, int]]] = defaultdict(list)  # key -> list of (row_idx, year_start, year_end)

    for row_idx, row in enumerate(rows):
        name = (row.get('name') or '').strip()
        lon_str = (row.get('lon') or '').strip()
        lat_str = (row.get('lat') or '').strip()
        year_start_str = (row.get('year_start') or '').strip()
        year_end_str = (row.get('year_end') or '').strip()
        importance_str = (row.get('importance') or '').strip()

        # Check 10: importance in [1, 10]
        if importance_str:
            try:
                imp_val = float(importance_str)
                if not (1 <= imp_val <= 10):
                    result.errors.append(
                        f"Row {row_idx + 2}: importance={importance_str} is out of range [1, 10]"
                    )
            except (TypeError, ValueError):
                result.errors.append(
                    f"Row {row_idx + 2}: importance must be numeric, got {importance_str!r}"
                )

        # Check 11: lon/lat bounds
        lon = None
        lat = None
        if lon_str:
            try:
                lon = float(lon_str)
                if not (-180 <= lon <= 180):
                    result.errors.append(
                        f"Row {row_idx + 2}: lon={lon} out of bounds [-180, 180]"
                    )
            except ValueError:
                result.errors.append(
                    f"Row {row_idx + 2}: lon must be numeric, got {lon_str!r}"
                )
        if lat_str:
            try:
                lat = float(lat_str)
                if not (-90 <= lat <= 90):
                    result.errors.append(
                        f"Row {row_idx + 2}: lat={lat} out of bounds [-90, 90]"
                    )
            except ValueError:
                result.errors.append(
                    f"Row {row_idx + 2}: lat must be numeric, got {lat_str!r}"
                )

        # Check 12: year_start < year_end when year_end is not null/empty
        year_start = None
        year_end = None
        if year_start_str:
            try:
                year_start = int(year_start_str)
            except ValueError:
                result.errors.append(
                    f"Row {row_idx + 2}: year_start must be integer, got {year_start_str!r}"
                )
        if year_end_str:
            try:
                year_end = int(year_end_str)
            except ValueError:
                result.errors.append(
                    f"Row {row_idx + 2}: year_end must be integer, got {year_end_str!r}"
                )
        if year_start is not None and year_end is not None:
            if year_start >= year_end:
                result.errors.append(
                    f"Row {row_idx + 2}: year_start ({year_start}) must be < year_end ({year_end})"
                )

        # Accumulate for duplicate/overlap check (check 9)
        if lon is not None and lat is not None and name:
            key = (lon, lat, name)
            groups[key].append((row_idx + 2, year_start, year_end))

    # Check 9: No two rows share (lon, lat, name) with overlapping time ranges
    for key, entries in groups.items():
        if len(entries) < 2:
            continue
        lon_k, lat_k, name_k = key
        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                row_i, ys_i, ye_i = entries[i]
                row_j, ys_j, ye_j = entries[j]
                # Treat None year_end as open-ended (use a large number)
                _ye_i = ye_i if ye_i is not None else 9999
                _ye_j = ye_j if ye_j is not None else 9999
                _ys_i = ys_i if ys_i is not None else -9999
                _ys_j = ys_j if ys_j is not None else -9999
                # Ranges overlap if max(start) < min(end)
                if max(_ys_i, _ys_j) < min(_ye_i, _ye_j):
                    result.errors.append(
                        f"Rows {row_i} and {row_j}: duplicate (lon={lon_k}, lat={lat_k}, "
                        f"name={name_k!r}) with overlapping time ranges "
                        f"[{ys_i},{ye_i}] and [{ys_j},{ye_j}]"
                    )

    return result


def validate_all_geojson(base_dir: Path | str = "data/raw/political") -> list[ValidationResult]:
    """Validate all phase-N.geojson files under base_dir recursively."""
    base_dir = Path(base_dir)
    results = []
    for geojson_path in sorted(base_dir.glob('**/*.geojson')):
        results.append(validate_geojson_file(geojson_path))
    return results


def print_results(results: list[ValidationResult]) -> int:
    """Print validation results. Returns exit code (0=clean, 1=errors)."""
    has_errors = False
    for result in results:
        if result.errors or result.warnings:
            print(f"\n{'ERROR' if result.errors else 'WARN'}: {result.path}")
        for warning in result.warnings:
            print(f"  WARN  {warning}")
        for error in result.errors:
            print(f"  ERROR {error}")
            has_errors = True

    total = len(results)
    error_count = sum(1 for r in results if not r.ok)
    warn_count = sum(1 for r in results if r.warnings and r.ok)
    clean_count = total - error_count - warn_count

    print(
        f"\nValidated {total} file(s): "
        f"{clean_count} clean, {warn_count} warnings-only, {error_count} with errors."
    )
    return 1 if has_errors else 0
