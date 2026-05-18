import json
import textwrap
from pathlib import Path

import pytest
import yaml

from data.validate import (
    ValidationResult,
    validate_geojson_file,
    validate_place_names_csv,
    validate_all_geojson,
    print_results,
)


def _write_geojson(path: Path, feature_props: dict, coords=None) -> None:
    if coords is None:
        coords = [[[[8.0, 44.0], [10.0, 44.0], [10.0, 46.0], [8.0, 46.0], [8.0, 44.0]]]]
    data = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {"type": "MultiPolygon", "coordinates": coords},
            "properties": feature_props,
        }],
    }
    path.write_text(json.dumps(data), encoding="utf-8")


def _write_yaml(entities_dir: Path, slug: str, color: str = "#c0392b") -> None:
    entities_dir.mkdir(parents=True, exist_ok=True)
    (entities_dir / f"{slug}.yml").write_text(
        yaml.dump({"slug": slug, "type": "empire", "color": color}),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# GeoJSON validation
# ---------------------------------------------------------------------------

class TestValidateGeoJSON:
    def test_valid_file_passes(self, tmp_path, monkeypatch):
        slug = "test-empire"
        phase_dir = tmp_path / slug
        phase_dir.mkdir()
        entities_dir = tmp_path / "entities"
        _write_yaml(entities_dir, slug)
        _write_geojson(phase_dir / "phase-1.geojson", {})

        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", entities_dir)

        result = validate_geojson_file(phase_dir / "phase-1.geojson")
        assert result.ok
        assert result.errors == []

    def test_year_start_after_year_end_is_error(self, tmp_path, monkeypatch):
        slug = "test-empire"
        phase_dir = tmp_path / slug
        phase_dir.mkdir()
        _write_geojson(phase_dir / "phase-1.geojson", {"year_start": 100, "year_end": 50})

        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

        result = validate_geojson_file(phase_dir / "phase-1.geojson")
        assert not result.ok
        assert any("year_start" in e for e in result.errors)

    def test_year_start_equal_year_end_is_error(self, tmp_path, monkeypatch):
        slug = "test-empire"
        phase_dir = tmp_path / slug
        phase_dir.mkdir()
        _write_geojson(phase_dir / "phase-1.geojson", {"year_start": 100, "year_end": 100})

        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

        result = validate_geojson_file(phase_dir / "phase-1.geojson")
        assert not result.ok

    def test_invalid_color_in_yaml_is_error(self, tmp_path, monkeypatch):
        slug = "test-empire"
        phase_dir = tmp_path / slug
        phase_dir.mkdir()
        entities_dir = tmp_path / "entities"
        _write_yaml(entities_dir, slug, color="#GGGGGG")
        _write_geojson(phase_dir / "phase-1.geojson", {})

        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", entities_dir)

        result = validate_geojson_file(phase_dir / "phase-1.geojson")
        assert not result.ok
        assert any("color" in e for e in result.errors)

    def test_importance_out_of_range_high_is_error(self, tmp_path, monkeypatch):
        slug = "test-empire"
        phase_dir = tmp_path / slug
        phase_dir.mkdir()
        _write_geojson(phase_dir / "phase-1.geojson", {"importance": 15})

        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

        result = validate_geojson_file(phase_dir / "phase-1.geojson")
        assert not result.ok
        assert any("importance" in e for e in result.errors)

    def test_importance_out_of_range_zero_is_error(self, tmp_path, monkeypatch):
        slug = "test-empire"
        phase_dir = tmp_path / slug
        phase_dir.mkdir()
        _write_geojson(phase_dir / "phase-1.geojson", {"importance": 0})

        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

        result = validate_geojson_file(phase_dir / "phase-1.geojson")
        assert not result.ok

    def test_invalid_confidence_type_is_error(self, tmp_path, monkeypatch):
        slug = "test-empire"
        phase_dir = tmp_path / slug
        phase_dir.mkdir()
        _write_geojson(phase_dir / "phase-1.geojson", {"confidence_type": "unknown"})

        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

        result = validate_geojson_file(phase_dir / "phase-1.geojson")
        assert not result.ok
        assert any("confidence_type" in e for e in result.errors)

    def test_invalid_date_precision_is_error(self, tmp_path, monkeypatch):
        slug = "test-empire"
        phase_dir = tmp_path / slug
        phase_dir.mkdir()
        _write_geojson(phase_dir / "phase-1.geojson", {"date_precision": "vague"})

        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

        result = validate_geojson_file(phase_dir / "phase-1.geojson")
        assert not result.ok
        assert any("date_precision" in e for e in result.errors)

    def test_out_of_bounds_lon_is_error(self, tmp_path, monkeypatch):
        slug = "test-empire"
        phase_dir = tmp_path / slug
        phase_dir.mkdir()
        bad_coords = [[[[200.0, 44.0], [201.0, 44.0], [201.0, 46.0], [200.0, 46.0], [200.0, 44.0]]]]
        _write_geojson(phase_dir / "phase-1.geojson", {}, coords=bad_coords)

        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

        result = validate_geojson_file(phase_dir / "phase-1.geojson")
        assert not result.ok
        assert any("lon" in e for e in result.errors)

    def test_out_of_bounds_lat_is_error(self, tmp_path, monkeypatch):
        slug = "test-empire"
        phase_dir = tmp_path / slug
        phase_dir.mkdir()
        bad_coords = [[[[8.0, 95.0], [10.0, 95.0], [10.0, 96.0], [8.0, 96.0], [8.0, 95.0]]]]
        _write_geojson(phase_dir / "phase-1.geojson", {}, coords=bad_coords)

        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

        result = validate_geojson_file(phase_dir / "phase-1.geojson")
        assert not result.ok
        assert any("lat" in e for e in result.errors)

    def test_missing_source_license_is_warning_not_error(self, tmp_path, monkeypatch):
        slug = "test-empire"
        phase_dir = tmp_path / slug
        phase_dir.mkdir()
        _write_geojson(phase_dir / "phase-1.geojson", {})  # no source_license

        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

        result = validate_geojson_file(phase_dir / "phase-1.geojson")
        assert result.ok  # warning, not error
        assert any("source_license" in w for w in result.warnings)

    def test_valid_confidence_types_pass(self, tmp_path, monkeypatch):
        for ct in ("exact", "approximate", "inferred", "disputed"):
            slug = "test-empire"
            phase_dir = tmp_path / slug
            phase_dir.mkdir(exist_ok=True)
            _write_geojson(phase_dir / "phase-1.geojson", {"confidence_type": ct})

            import data.validate as v
            monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

            result = validate_geojson_file(phase_dir / "phase-1.geojson")
            assert not any("confidence_type" in e for e in result.errors), ct

    def test_corrupted_json_is_error(self, tmp_path, monkeypatch):
        slug = "test-empire"
        phase_dir = tmp_path / slug
        phase_dir.mkdir()
        (phase_dir / "phase-1.geojson").write_text("not json", encoding="utf-8")

        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

        result = validate_geojson_file(phase_dir / "phase-1.geojson")
        assert not result.ok


class TestValidateAll:
    def test_returns_list_of_results(self, tmp_path, monkeypatch):
        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

        (tmp_path / "rome").mkdir()
        _write_geojson(tmp_path / "rome" / "phase-1.geojson", {})
        (tmp_path / "carthage").mkdir()
        _write_geojson(tmp_path / "carthage" / "phase-1.geojson", {})

        results = validate_all_geojson(tmp_path)
        assert len(results) == 2
        assert all(isinstance(r, ValidationResult) for r in results)

    def test_one_invalid_one_valid(self, tmp_path, monkeypatch):
        import data.validate as v
        monkeypatch.setattr(v, "_ENTITIES_DIR", tmp_path / "entities")

        (tmp_path / "valid").mkdir()
        _write_geojson(tmp_path / "valid" / "phase-1.geojson", {})
        (tmp_path / "invalid").mkdir()
        _write_geojson(tmp_path / "invalid" / "phase-1.geojson", {"year_start": 100, "year_end": 50})

        results = validate_all_geojson(tmp_path)
        ok_count = sum(1 for r in results if r.ok)
        err_count = sum(1 for r in results if not r.ok)
        assert ok_count == 1
        assert err_count == 1


class TestPrintResults:
    def test_returns_0_on_clean(self, capsys):
        results = [ValidationResult(path="f.geojson")]
        code = print_results(results)
        assert code == 0

    def test_returns_1_on_errors(self, capsys):
        r = ValidationResult(path="f.geojson", errors=["bad thing"])
        code = print_results([r])
        assert code == 1


# ---------------------------------------------------------------------------
# Place names CSV validation
# ---------------------------------------------------------------------------

class TestValidatePlaceNames:
    def _write_csv(self, path: Path, rows: list[dict]) -> None:
        import csv
        fieldnames = ["name", "lon", "lat", "year_start", "year_end", "importance", "type"]
        with path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def test_valid_csv_passes(self, tmp_path):
        csv_path = tmp_path / "cities.csv"
        self._write_csv(csv_path, [
            {"name": "Rome", "lon": "12.5", "lat": "41.9",
             "year_start": "-500", "year_end": "500", "importance": "10", "type": "city"},
        ])
        result = validate_place_names_csv(csv_path)
        assert result.ok

    def test_duplicate_with_overlap_is_error(self, tmp_path):
        csv_path = tmp_path / "cities.csv"
        self._write_csv(csv_path, [
            {"name": "Rome", "lon": "12.5", "lat": "41.9",
             "year_start": "-500", "year_end": "200", "importance": "10", "type": "city"},
            {"name": "Rome", "lon": "12.5", "lat": "41.9",
             "year_start": "-100", "year_end": "300", "importance": "10", "type": "city"},
        ])
        result = validate_place_names_csv(csv_path)
        assert not result.ok
        assert any("duplicate" in e.lower() for e in result.errors)

    def test_duplicate_no_overlap_passes(self, tmp_path):
        csv_path = tmp_path / "cities.csv"
        self._write_csv(csv_path, [
            {"name": "Constantinople", "lon": "28.97", "lat": "41.01",
             "year_start": "330", "year_end": "1453", "importance": "10", "type": "city"},
            {"name": "Constantinople", "lon": "28.97", "lat": "41.01",
             "year_start": "1453", "year_end": "1923", "importance": "10", "type": "city"},
        ])
        result = validate_place_names_csv(csv_path)
        assert result.ok

    def test_importance_out_of_range_is_error(self, tmp_path):
        csv_path = tmp_path / "cities.csv"
        self._write_csv(csv_path, [
            {"name": "X", "lon": "10", "lat": "40",
             "year_start": "0", "year_end": "", "importance": "0", "type": "city"},
        ])
        result = validate_place_names_csv(csv_path)
        assert not result.ok

    def test_lon_out_of_bounds_is_error(self, tmp_path):
        csv_path = tmp_path / "cities.csv"
        self._write_csv(csv_path, [
            {"name": "X", "lon": "200", "lat": "40",
             "year_start": "0", "year_end": "", "importance": "5", "type": "city"},
        ])
        result = validate_place_names_csv(csv_path)
        assert not result.ok

    def test_lat_out_of_bounds_is_error(self, tmp_path):
        csv_path = tmp_path / "cities.csv"
        self._write_csv(csv_path, [
            {"name": "X", "lon": "10", "lat": "95",
             "year_start": "0", "year_end": "", "importance": "5", "type": "city"},
        ])
        result = validate_place_names_csv(csv_path)
        assert not result.ok

    def test_year_start_after_year_end_is_error(self, tmp_path):
        csv_path = tmp_path / "cities.csv"
        self._write_csv(csv_path, [
            {"name": "X", "lon": "10", "lat": "40",
             "year_start": "500", "year_end": "100", "importance": "5", "type": "city"},
        ])
        result = validate_place_names_csv(csv_path)
        assert not result.ok
