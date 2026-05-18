"""Tests for audit_entity_types.py — entity type conformance validation."""

import textwrap
from pathlib import Path

import pytest
from data.audit_entity_types import (
    VALID_ENTITY_TYPES,
    audit_entity_files,
    run_audit,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_entity(tmp_path: Path, slug: str, entity_type: str) -> Path:
    """Write a minimal entity YAML and return its path."""
    content = textwrap.dedent(f"""\
        slug: {slug}
        name: Test Entity
        type: {entity_type}
        color: "#000000"
        year_start: -100
        year_end: 100
    """)
    yml = tmp_path / f"{slug}.yml"
    yml.write_text(content, encoding="utf-8")
    return yml


# ---------------------------------------------------------------------------
# Unit tests — audit_entity_files()
# ---------------------------------------------------------------------------

class TestAuditEntityFiles:
    def test_conforming_type_passes(self, tmp_path):
        _write_entity(tmp_path, "test-empire", "empire")
        conforming, violations = audit_entity_files(tmp_path)
        assert len(conforming) == 1
        assert len(violations) == 0
        assert conforming[0]["slug"] == "test-empire"
        assert conforming[0]["type"] == "empire"

    def test_nonconforming_polity_is_violation(self, tmp_path):
        _write_entity(tmp_path, "old-entity", "polity")
        conforming, violations = audit_entity_files(tmp_path)
        assert len(conforming) == 0
        assert len(violations) == 1
        assert violations[0]["slug"] == "old-entity"
        assert violations[0]["type"] == "polity"

    def test_unknown_type_is_violation(self, tmp_path):
        _write_entity(tmp_path, "weird-entity", "weird_type")
        conforming, violations = audit_entity_files(tmp_path)
        assert len(violations) == 1

    def test_mixed_files(self, tmp_path):
        _write_entity(tmp_path, "good", "kingdom")
        _write_entity(tmp_path, "bad", "polity")
        conforming, violations = audit_entity_files(tmp_path)
        assert len(conforming) == 1
        assert len(violations) == 1

    def test_empty_directory(self, tmp_path):
        conforming, violations = audit_entity_files(tmp_path)
        assert conforming == []
        assert violations == []

    @pytest.mark.parametrize("entity_type", sorted(VALID_ENTITY_TYPES))
    def test_all_valid_taxonomy_types_pass(self, tmp_path, entity_type):
        """Every type in VALID_ENTITY_TYPES must be accepted as conforming."""
        _write_entity(tmp_path, f"entity-{entity_type}", entity_type)
        conforming, violations = audit_entity_files(tmp_path)
        assert len(conforming) == 1
        assert len(violations) == 0


# ---------------------------------------------------------------------------
# Integration tests — run_audit() exit code
# ---------------------------------------------------------------------------

class TestRunAudit:
    def test_exit_code_0_on_all_conforming(self, tmp_path):
        _write_entity(tmp_path, "good-empire", "empire")
        _write_entity(tmp_path, "good-kingdom", "kingdom")
        code = run_audit(tmp_path)
        assert code == 0

    def test_exit_code_1_on_any_violation(self, tmp_path):
        _write_entity(tmp_path, "good-empire", "empire")
        _write_entity(tmp_path, "bad-polity", "polity")
        code = run_audit(tmp_path)
        assert code == 1

    def test_exit_code_1_single_violation(self, tmp_path):
        _write_entity(tmp_path, "bad-entity", "polity")
        code = run_audit(tmp_path)
        assert code == 1

    def test_exit_code_0_empty_directory(self, tmp_path):
        code = run_audit(tmp_path)
        assert code == 0


# ---------------------------------------------------------------------------
# Regression: all 13 production entity YAMLs must now conform
# ---------------------------------------------------------------------------

class TestProductionEntityFiles:
    def test_all_production_entities_conform(self):
        """All entity YAMLs in packages/data/entities/ must pass the M3 taxonomy."""
        entities_dir = Path(__file__).parents[1] / "entities"
        if not entities_dir.exists():
            pytest.skip(f"Entities directory not found: {entities_dir}")

        conforming, violations = audit_entity_files(entities_dir)

        if violations:
            msgs = [f"  {v['slug']}: type={v['type']!r}" for v in violations]
            pytest.fail(
                f"Entity YAML type violations found:\n" + "\n".join(msgs)
            )

        assert len(conforming) > 0, "No entity files found — check path"
