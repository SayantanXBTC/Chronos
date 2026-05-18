"""Tests for fetch_sources.py — Task 12 (M3-C).

Uses unittest.mock to avoid real HTTP calls.
"""

from __future__ import annotations

import hashlib
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Path to the registry used by production code
_REPO_ROOT = Path(__file__).parent.parent.parent.parent
REGISTRY_PATH = _REPO_ROOT / "packages" / "data" / "sources" / "registry.yaml"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Tests: registry.yaml integrity
# ---------------------------------------------------------------------------

class TestRegistryYaml:
    """Test 8: registry.yaml is valid YAML with expected structure."""

    def test_registry_yaml_parses(self):
        """registry.yaml is valid YAML, top-level key is 'sources', it's a list."""
        assert REGISTRY_PATH.exists(), f"registry.yaml not found at {REGISTRY_PATH}"
        with REGISTRY_PATH.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        assert "sources" in data, "Top-level key 'sources' missing"
        assert isinstance(data["sources"], list), "'sources' must be a list"
        assert len(data["sources"]) > 0, "'sources' list must not be empty"

    def test_load_registry_finds_cshapes(self):
        """Test 1: load registry.yaml and find cshapes-2.0 entry."""
        with REGISTRY_PATH.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        ids = [s["id"] for s in data["sources"]]
        assert "cshapes-2.0" in ids, f"cshapes-2.0 not in registry ids: {ids}"

    def test_load_registry_has_required_fields(self):
        """Test 2: all entries have id/name/license/format."""
        required = {"id", "name", "license", "format"}
        with REGISTRY_PATH.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        for entry in data["sources"]:
            missing = required - entry.keys()
            assert not missing, (
                f"Entry '{entry.get('id', '?')}' is missing fields: {missing}"
            )

    def test_registry_has_three_sources(self):
        """Registry contains exactly the 3 expected sources."""
        with REGISTRY_PATH.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        ids = {s["id"] for s in data["sources"]}
        assert ids == {"cshapes-2.0", "awmc-barrington", "natural-earth-physical"}


# ---------------------------------------------------------------------------
# Tests: fetch_source behaviour
# ---------------------------------------------------------------------------

class TestFetchSource:
    """Tests for fetch_sources.fetch_source()."""

    def test_fetch_source_skips_null_url(self, tmp_path):
        """Test 3: raises ValueError when url is null."""
        from data.fetch_sources import fetch_source

        with pytest.raises(ValueError, match="manual download required"):
            fetch_source(
                "awmc-barrington",
                registry_path=REGISTRY_PATH,
                dest_dir=tmp_path,
            )

    def test_fetch_source_unknown_id_raises(self, tmp_path):
        """Test 7: fetch_source('nonexistent', ...) raises ValueError."""
        from data.fetch_sources import fetch_source

        with pytest.raises(ValueError, match="nonexistent"):
            fetch_source(
                "nonexistent",
                registry_path=REGISTRY_PATH,
                dest_dir=tmp_path,
            )

    def test_fetch_source_skip_if_already_downloaded(self, tmp_path):
        """Test 4: file exists + sha256 is null in registry → no HTTP call made."""
        from data.fetch_sources import fetch_source

        # Pre-create the target file so it looks already downloaded
        source_id = "cshapes-2.0"
        target_rel = "cshapes/cshapes_2.0.shp"
        target_path = tmp_path / source_id / target_rel
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(b"fake shapefile content")

        with patch("urllib.request.urlretrieve") as mock_retrieve:
            result = fetch_source(
                source_id,
                registry_path=REGISTRY_PATH,
                dest_dir=tmp_path,
            )
        # urlretrieve must NOT have been called
        mock_retrieve.assert_not_called()
        assert result == target_path

    def test_sha256_mismatch_raises(self, tmp_path):
        """Test 5: file exists but sha256 mismatch → raises ValueError."""
        from data.fetch_sources import fetch_source

        # Build a custom registry entry with a known sha256 that won't match
        fake_sha = "a" * 64  # wrong hash

        # We patch _load_registry to inject a custom entry with a bad sha256
        source_id = "cshapes-2.0"
        fake_entry = {
            "id": source_id,
            "name": "cShapes 2.0",
            "url": "https://example.com/cshapes_2.0.zip",
            "sha256": fake_sha,
            "license": "CC BY",
            "format": "shapefile",
            "config": "packages/data/sources/cshapes.yml",
            "target_file": "cshapes/cshapes_2.0.shp",
            "temporal_range": "1886-2019 CE",
            "notes": "",
        }

        # Pre-create a zip archive as the "downloaded" file so we skip the HTTP call
        archive_path = tmp_path / source_id / "cshapes_2.0.zip"
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        fake_content = b"fake zip content that does not match sha256"
        with zipfile.ZipFile(archive_path, "w") as zf:
            zf.writestr("cshapes/cshapes_2.0.shp", "fake shapefile")
        archive_bytes = archive_path.read_bytes()
        real_sha = _sha256(archive_bytes)
        # Confirm our fake_sha is actually different
        assert fake_sha != real_sha

        import data.fetch_sources as fs_mod

        with patch.object(fs_mod, "_load_registry", return_value=[fake_entry]):
            with patch("urllib.request.urlretrieve") as mock_retrieve:
                with pytest.raises(ValueError, match="SHA-256 mismatch"):
                    fetch_source(
                        source_id,
                        registry_path=REGISTRY_PATH,
                        dest_dir=tmp_path,
                        verify_sha256=True,
                    )

    def test_fetch_source_downloads_and_extracts_zip(self, tmp_path):
        """Successful download of a .zip source is extracted and target_file returned."""
        from data.fetch_sources import fetch_source

        source_id = "cshapes-2.0"
        target_rel = "cshapes/cshapes_2.0.shp"

        # Build a real zip in a temp location to serve as the downloaded file
        fake_zip = tmp_path / "_fake_download.zip"
        with zipfile.ZipFile(fake_zip, "w") as zf:
            zf.writestr(target_rel, "shapefile data")
        zip_bytes = fake_zip.read_bytes()
        real_sha = _sha256(zip_bytes)

        fake_entry = {
            "id": source_id,
            "name": "cShapes 2.0",
            "url": "https://example.com/cshapes_2.0.zip",
            "sha256": None,
            "license": "CC BY",
            "format": "shapefile",
            "config": "packages/data/sources/cshapes.yml",
            "target_file": target_rel,
            "temporal_range": "1886-2019 CE",
            "notes": "",
        }

        import data.fetch_sources as fs_mod

        def fake_urlretrieve(url, dest, reporthook=None):
            # Copy our pre-built zip to the destination
            Path(dest).write_bytes(zip_bytes)

        with patch.object(fs_mod, "_load_registry", return_value=[fake_entry]):
            with patch("urllib.request.urlretrieve", side_effect=fake_urlretrieve):
                result = fetch_source(
                    source_id,
                    registry_path=REGISTRY_PATH,
                    dest_dir=tmp_path,
                    verify_sha256=False,
                )

        expected = tmp_path / source_id / target_rel
        assert result == expected
        assert result.exists()
        assert result.read_text() == "shapefile data"


# ---------------------------------------------------------------------------
# Tests: fetch_all_sources
# ---------------------------------------------------------------------------

class TestFetchAllSources:
    """Tests for fetch_sources.fetch_all_sources()."""

    def test_fetch_all_skips_null_url_sources(self, tmp_path):
        """Test 6: fetch_all skips sources with url=null (awmc-barrington), no error."""
        from data.fetch_sources import fetch_all_sources

        # Create fake entries: one with url, one without
        fake_entries = [
            {
                "id": "awmc-barrington",
                "name": "AWMC",
                "url": None,
                "sha256": None,
                "license": "CC BY 4.0",
                "format": "shapefile",
                "config": "packages/data/sources/awmc.yml",
                "target_file": None,
                "temporal_range": "500 BCE – 500 CE",
                "notes": "",
            },
        ]

        import data.fetch_sources as fs_mod

        with patch.object(fs_mod, "_load_registry", return_value=fake_entries):
            # Should not raise — null-url sources are skipped
            results = fetch_all_sources(
                registry_path=REGISTRY_PATH,
                dest_dir=tmp_path,
            )

        assert results == [], "No results expected when all sources have null URL"

    def test_fetch_all_returns_paths_for_url_sources(self, tmp_path):
        """fetch_all returns Path objects for sources with URLs that succeed."""
        from data.fetch_sources import fetch_all_sources

        source_id = "natural-earth-physical"
        target_rel = "ne_10m_rivers_lake_centerlines/ne_10m_rivers_lake_centerlines.shp"

        fake_zip = tmp_path / "_ne_fake.zip"
        with zipfile.ZipFile(fake_zip, "w") as zf:
            zf.writestr(target_rel, "river data")
        zip_bytes = fake_zip.read_bytes()

        fake_entries = [
            {
                "id": source_id,
                "name": "Natural Earth Physical Vectors",
                "url": "https://example.com/ne_rivers.zip",
                "sha256": None,
                "license": "Public Domain",
                "format": "shapefile",
                "config": None,
                "target_file": target_rel,
                "temporal_range": "Modern",
                "notes": "",
            },
        ]

        import data.fetch_sources as fs_mod

        def fake_urlretrieve(url, dest, reporthook=None):
            Path(dest).write_bytes(zip_bytes)

        with patch.object(fs_mod, "_load_registry", return_value=fake_entries):
            with patch("urllib.request.urlretrieve", side_effect=fake_urlretrieve):
                results = fetch_all_sources(
                    registry_path=REGISTRY_PATH,
                    dest_dir=tmp_path,
                    verify_sha256=False,
                )

        assert len(results) == 1
        assert results[0] == tmp_path / source_id / target_rel
