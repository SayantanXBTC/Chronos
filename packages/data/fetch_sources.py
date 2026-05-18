"""fetch_sources.py — Download external data sources defined in registry.yaml.

Uses stdlib only (urllib.request, hashlib, zipfile). No requests/httpx.
"""

from __future__ import annotations

import hashlib
import urllib.request
import yaml
import zipfile
from pathlib import Path


# Default destination relative to repo root
_DEFAULT_DEST = Path(__file__).parent.parent.parent / "data" / "sources"


def _load_registry(registry_path: Path) -> list[dict]:
    """Parse registry.yaml and return the list of source entries."""
    with registry_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data["sources"]


def _find_source(sources: list[dict], source_id: str) -> dict:
    """Return the source entry matching source_id, or raise ValueError."""
    for entry in sources:
        if entry["id"] == source_id:
            return entry
    raise ValueError(
        f"Source '{source_id}' not found in registry. "
        f"Available ids: {[s['id'] for s in sources]}"
    )


def _sha256_of_file(path: Path) -> str:
    """Compute hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _download_with_progress(url: str, dest: Path) -> None:
    """Download url to dest, printing progress."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"  Downloading {url}")
    downloaded = 0

    def _reporthook(block_num: int, block_size: int, total_size: int) -> None:
        nonlocal downloaded
        downloaded = block_num * block_size
        if total_size > 0:
            pct = min(100, downloaded * 100 // total_size)
            print(f"\r  {downloaded:,} / {total_size:,} bytes ({pct}%)", end="", flush=True)
        else:
            print(f"\r  {downloaded:,} bytes", end="", flush=True)

    urllib.request.urlretrieve(url, dest, reporthook=_reporthook)
    print()  # newline after progress
    print(f"  Saved to {dest}")


def fetch_source(
    source_id: str,
    registry_path: Path,
    dest_dir: Path,
    *,
    verify_sha256: bool = True,
) -> Path:
    """Download a source from registry by id. Returns path to extracted/downloaded file.

    - Loads registry.yaml
    - Finds source by id
    - If source.url is None: raises ValueError (manual download required, print note)
    - Downloads to dest_dir/<source_id>/<filename>
    - If already downloaded (file exists, sha256 matches if known): skip re-download (idempotent)
    - If sha256 in registry is not None: verify after download, raise ValueError on mismatch
    - If file is .zip: extract to dest_dir/<source_id>/
    - Returns Path to target_file within dest_dir/<source_id>/
    """
    sources = _load_registry(registry_path)
    entry = _find_source(sources, source_id)

    url: str | None = entry.get("url")
    expected_sha256: str | None = entry.get("sha256")
    target_file: str | None = entry.get("target_file")
    config: str | None = entry.get("config")

    if url is None:
        msg = (
            f"Source '{source_id}': manual download required. "
            f"See {config or 'registry for instructions'}."
        )
        print(msg)
        raise ValueError(msg)

    source_dir = dest_dir / source_id
    source_dir.mkdir(parents=True, exist_ok=True)

    # Determine archive filename from URL
    archive_name = url.split("/")[-1]
    archive_path = source_dir / archive_name

    # --- Idempotency check ---
    # If target_file is set, check if it already exists with matching sha256.
    final_path: Path | None = None
    if target_file:
        final_path = source_dir / target_file
        if final_path.exists():
            if expected_sha256 is None or not verify_sha256:
                print(f"Source '{source_id}': already downloaded at {final_path}, skipping.")
                return final_path
            # Verify existing file
            actual = _sha256_of_file(final_path)
            if actual == expected_sha256:
                print(f"Source '{source_id}': already downloaded and verified, skipping.")
                return final_path
            # sha256 mismatch on existing file — re-download
            print(f"Source '{source_id}': sha256 mismatch on existing file, re-downloading.")

    # Also check if archive already on disk (and sha256 matches) before downloading
    if archive_path.exists() and (expected_sha256 is None or not verify_sha256):
        print(f"Source '{source_id}': archive already present at {archive_path}.")
    elif archive_path.exists() and expected_sha256 is not None and verify_sha256:
        actual = _sha256_of_file(archive_path)
        if actual == expected_sha256:
            print(f"Source '{source_id}': archive already downloaded and verified, skipping download.")
        else:
            _download_with_progress(url, archive_path)
    else:
        _download_with_progress(url, archive_path)

    # --- SHA-256 verification of downloaded archive ---
    if expected_sha256 is not None and verify_sha256:
        actual = _sha256_of_file(archive_path)
        if actual != expected_sha256:
            raise ValueError(
                f"SHA-256 mismatch for '{source_id}'. "
                f"Expected {expected_sha256}, got {actual}."
            )
        print(f"  SHA-256 verified OK.")

    # --- Extraction ---
    if archive_path.suffix.lower() == ".zip":
        print(f"  Extracting {archive_path} -> {source_dir}/")
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(source_dir)

    # --- Return target path ---
    if target_file:
        final_path = source_dir / target_file
        return final_path

    # No target_file specified — return the archive itself (or source_dir)
    return archive_path


def fetch_all_sources(
    registry_path: Path,
    dest_dir: Path,
    *,
    verify_sha256: bool = True,
) -> list[Path]:
    """Fetch all sources in registry that have a URL.

    Sources with url=null are skipped (manual download required).
    Returns list of paths to successfully downloaded/extracted files.
    """
    sources = _load_registry(registry_path)
    results: list[Path] = []

    for entry in sources:
        source_id = entry["id"]
        url = entry.get("url")
        config = entry.get("config")

        if url is None:
            print(
                f"Source '{source_id}': manual download required. "
                f"See {config or 'registry for instructions'}."
            )
            continue

        try:
            path = fetch_source(
                source_id,
                registry_path=registry_path,
                dest_dir=dest_dir,
                verify_sha256=verify_sha256,
            )
            results.append(path)
        except ValueError as exc:
            print(f"Source '{source_id}': ERROR — {exc}")

    return results
