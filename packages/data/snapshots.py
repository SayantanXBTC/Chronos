import asyncio
import json
import os
from pathlib import Path

import httpx

SNAPSHOT_YEARS = [y for y in range(-500, 501, 25) if y != 0]

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
SNAPSHOT_DIR = os.getenv(
    "SNAPSHOT_DIR",
    str(Path(__file__).parent.parent.parent / "data" / "snapshots" / "political"),
)
OUTPUT_DIR = Path(SNAPSHOT_DIR)


async def compute_snapshot(client: httpx.AsyncClient, year: int) -> dict:
    """Fetch a snapshot from the API for a given year."""
    url = f"{API_BASE_URL}/api/v1/world/state"
    params = {
        "year": year,
        "zoom": 4,
        "min_x": -180,
        "min_y": -90,
        "max_x": 180,
        "max_y": 90,
    }
    response = await client.get(url, params=params, timeout=30.0)
    response.raise_for_status()
    return response.json()


async def run_snapshot_generation() -> None:
    """Generate snapshots for all SNAPSHOT_YEARS."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with httpx.AsyncClient() as client:
        total = len(SNAPSHOT_YEARS)
        generated = 0
        skipped = 0

        for year in SNAPSHOT_YEARS:
            output_file = OUTPUT_DIR / f"{year}.json"

            if output_file.exists():
                print(f"Skip {year} (exists)")
                skipped += 1
                continue

            snapshot = await compute_snapshot(client, year)
            with open(output_file, "w") as f:
                json.dump(snapshot, f)
            generated += 1
            print(f"Generated snapshot for year {year}")

        print(
            f"\nSnapshot generation complete: {generated} generated, {skipped} skipped, {total} total"
        )


if __name__ == "__main__":
    asyncio.run(run_snapshot_generation())
