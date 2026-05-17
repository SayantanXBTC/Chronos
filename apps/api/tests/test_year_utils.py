import pytest

from app.utils.year import display_to_year, snap_to_snapshot, year_to_display

pytestmark = pytest.mark.asyncio


def test_year_to_display_bce():
    assert year_to_display(-264) == "264 BCE"


def test_year_to_display_ce():
    assert year_to_display(117) == "117 CE"


def test_year_to_display_one_bce():
    assert year_to_display(-1) == "1 BCE"


def test_year_to_display_one_ce():
    assert year_to_display(1) == "1 CE"


def test_no_year_zero():
    with pytest.raises(ValueError, match="Year 0 does not exist"):
        year_to_display(0)


def test_display_to_year_bce():
    assert display_to_year("264 BCE") == -264


def test_display_to_year_ce():
    assert display_to_year("117 CE") == 117


def test_display_to_year_case_insensitive():
    assert display_to_year("264 bce") == -264


def test_display_to_year_bc_alias():
    assert display_to_year("264 BC") == -264


def test_display_to_year_ad_alias():
    assert display_to_year("117 AD") == 117


def test_snap_to_snapshot_rounds_down():
    snapshots = list(range(-500, 501, 25))
    snapshots = [y for y in snapshots if y != 0]
    assert snap_to_snapshot(-264, snapshots) == -275


def test_snap_to_snapshot_above_midpoint():
    snapshots = list(range(-500, 501, 25))
    snapshots = [y for y in snapshots if y != 0]
    assert snap_to_snapshot(-251, snapshots) == -275


def test_snap_to_snapshot_exact_match():
    snapshots = list(range(-500, 501, 25))
    snapshots = [y for y in snapshots if y != 0]
    assert snap_to_snapshot(-500, snapshots) == -500


def test_snap_to_snapshot_positive_year():
    snapshots = list(range(-500, 501, 25))
    snapshots = [y for y in snapshots if y != 0]
    assert snap_to_snapshot(100, snapshots) == 100


def test_snap_to_snapshot_raises_below_range():
    snapshots = list(range(-500, 501, 25))
    snapshots = [y for y in snapshots if y != 0]
    with pytest.raises(ValueError, match="before the earliest snapshot"):
        snap_to_snapshot(-600, snapshots)


def test_normalize_year_rejects_zero():
    from app.utils.year import normalize_year
    with pytest.raises(ValueError):
        normalize_year(0)


def test_normalize_year_passes_valid():
    from app.utils.year import normalize_year
    assert normalize_year(-264) == -264
    assert normalize_year(117) == 117
