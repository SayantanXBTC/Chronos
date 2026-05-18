"""
Seed region_coverage table with coverage metadata for all ingested regions.

Run from repo root:
  DATABASE_URL=postgresql://... python scripts/seed_region_coverage.py
"""
from __future__ import annotations

import os
import sys

import psycopg2

sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent.parent))
from packages.data.reporting import update_coverage

ROWS = [
    # (region_name, year_start, year_end, completeness, entity_count, primary_source, notes)
    (
        "Mediterranean", -800, 1453, "complete", 10,
        "Barrington Atlas / AWMC",
        "Roman, Greek, Carthaginian, and successor states fully represented",
    ),
    (
        "East Asia", -300, 1000, "partial", 3,
        "CHGIS / Tan Qixiang Historical Atlas",
        "Qin, Han, Tang ingested; Song, Ming, Yuan pending",
    ),
    (
        "South Asia", -350, 1857, "partial", 3,
        "Schwartzberg Historical Atlas",
        "Maurya, Gupta, Mughal ingested; Delhi Sultanate pending",
    ),
    (
        "Middle East", 600, 1923, "partial", 3,
        "Encyclopaedia of Islam / Ottoman surveys",
        "Umayyad, Abbasid, Ottoman ingested; Fatimid/Buyid pending",
    ),
    (
        "West Asia", -550, 651, "partial", 3,
        "Cambridge History of Iran",
        "Achaemenid, Parthian, Sasanian ingested",
    ),
    (
        "Africa", 1200, 1600, "sparse", 2,
        "UNESCO General History of Africa vol. IV",
        "Mali and Songhai ingested; Great Zimbabwe, Kanem-Bornu pending",
    ),
    (
        "Americas", 1400, 1533, "sparse", 2,
        "Smith (Aztecs) / D'Altroy (Incas)",
        "Aztec and Inca ingested; Maya Classic, Mississippian pending",
    ),
    (
        "Eurasia (Steppe)", 1206, 1368, "partial", 1,
        "Morgan — The Mongols",
        "Mongol Empire ingested; Khanate successor states pending",
    ),
]


def main() -> None:
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    db_url = db_url.replace("+asyncpg", "")

    conn = psycopg2.connect(db_url)
    try:
        for region_name, year_start, year_end, completeness, entity_count, source, notes in ROWS:
            update_coverage(
                conn,
                region_name=region_name,
                year_start=year_start,
                year_end=year_end,
                completeness=completeness,
                entity_count=entity_count,
                primary_source=source,
                notes=notes,
            )
            print(f"  upserted: {region_name} ({year_start}–{year_end}) [{completeness}]")
        print(f"\nDone: {len(ROWS)} region coverage rows upserted.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
