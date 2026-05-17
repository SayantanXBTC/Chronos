import bisect
import re


def year_to_display(year: int) -> str:
    """Convert internal integer year to display string. Negative = BCE."""
    if year == 0:
        raise ValueError("Year 0 does not exist in historical convention")
    if year < 0:
        return f"{abs(year)} BCE"
    return f"{year} CE"


def display_to_year(s: str) -> int:
    """Parse display string like '264 BCE' or '117 CE' to integer year."""
    s = s.strip().upper()
    match = re.fullmatch(r"(\d+)\s*(BCE|BC|CE|AD)", s)
    if not match:
        raise ValueError(f"Cannot parse year string: {s!r}")
    n = int(match.group(1))
    era = match.group(2)
    if era in ("BCE", "BC"):
        return -n
    return n


def normalize_year(year: int) -> int:
    """Validate year is non-zero. Raises ValueError for year 0."""
    if year == 0:
        raise ValueError("Year 0 does not exist in historical convention")
    return year


def snap_to_snapshot(year: int, snapshots: list[int]) -> int:
    """Return nearest snapshot year at or below the given year.

    Raises ValueError if year is below all snapshots.
    """
    if not snapshots:
        raise ValueError("Snapshot list is empty")
    sorted_snaps = sorted(snapshots)
    if year < sorted_snaps[0]:
        raise ValueError(
            f"Year {year} is before the earliest snapshot ({sorted_snaps[0]})"
        )
    idx = bisect.bisect_right(sorted_snaps, year) - 1
    idx = max(0, min(idx, len(sorted_snaps) - 1))
    return sorted_snaps[idx]
