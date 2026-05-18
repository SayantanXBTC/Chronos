#!/usr/bin/env python3
"""Pre-migration audit: check entity type conformance against M3 taxonomy.

Run before migration 0003:
    python packages/data/audit_entity_types.py

Reads entity YAML files, prints any types not in the valid taxonomy.
Does NOT connect to DB — validates source files only.
"""

import sys
from pathlib import Path

import yaml

from .constants import VALID_ENTITY_TYPES

# Default glob root: packages/data/entities relative to this file's package dir
_ENTITIES_DIR = Path(__file__).parent / "entities"


def audit_entity_files(entities_dir: Path = _ENTITIES_DIR) -> tuple[list[dict], list[dict]]:
    """Load all entity YAML files and split into conforming / violations.

    Returns:
        (conforming, violations) — each element is a dict with keys
        ``slug``, ``type``, and ``file``. Conforming entries have a valid
        taxonomy type; violation entries have either an unrecognised type
        or ``"<missing>"`` when the ``type`` key is absent from the YAML.
    """
    conforming: list[dict] = []
    violations: list[dict] = []

    for yml_path in sorted(entities_dir.glob("*.yml")):
        with yml_path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)

        slug = data.get("slug", yml_path.stem)
        entity_type = data.get("type")
        if entity_type is None:
            violations.append({
                "slug": slug,
                "type": "<missing>",
                "file": str(yml_path),
            })
            continue

        entry = {"slug": slug, "type": entity_type, "file": str(yml_path)}
        if entity_type in VALID_ENTITY_TYPES:
            conforming.append(entry)
        else:
            violations.append(entry)

    return conforming, violations


def run_audit(entities_dir: Path = _ENTITIES_DIR) -> int:
    """Run the audit, print results, and return exit code (0=clean, 1=violations)."""
    conforming, violations = audit_entity_files(entities_dir)

    print(f"Entity type audit — taxonomy: {sorted(VALID_ENTITY_TYPES)}\n")

    if conforming:
        print(f"Conforming ({len(conforming)}):")
        for entry in conforming:
            print(f"  OK  {entry['slug']!s:<30} type={entry['type']}")

    if violations:
        print(f"\nViolations ({len(violations)}):")
        for entry in violations:
            print(f"  !!  {entry['slug']!s:<30} type={entry['type']!r}  [{entry['file']}]")
        print(
            f"\n{len(violations)} violation(s) found. "
            "Update entity YAML files before running migration 0003."
        )
        return 1

    print(f"\nAll {len(conforming)} entity file(s) conform to the M3 taxonomy.")
    return 0


if __name__ == "__main__":
    sys.exit(run_audit())
