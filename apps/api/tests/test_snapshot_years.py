from app.services.world_state import SNAPSHOT_YEARS


def test_no_year_zero():
    assert 0 not in SNAPSHOT_YEARS


def test_starts_at_negative_3000():
    assert SNAPSHOT_YEARS[0] == -3000


def test_ends_at_2026():
    assert SNAPSHOT_YEARS[-1] == 2026


def test_strictly_ascending():
    assert SNAPSHOT_YEARS == sorted(SNAPSHOT_YEARS)


def test_no_duplicates():
    assert len(SNAPSHOT_YEARS) == len(set(SNAPSHOT_YEARS))


def test_approximate_count():
    # ~102 snapshots expected
    assert 90 <= len(SNAPSHOT_YEARS) <= 120


def test_boundary_density_ancient():
    # -3000 to -1000: 250-year intervals
    assert -3000 in SNAPSHOT_YEARS
    assert -2750 in SNAPSHOT_YEARS
    assert -1000 in SNAPSHOT_YEARS
    # should NOT have -2900 (not a 250-year boundary from -3000)
    assert -2900 not in SNAPSHOT_YEARS


def test_boundary_density_classical():
    # -500 to 500: 25-year intervals
    assert -500 in SNAPSHOT_YEARS
    assert -475 in SNAPSHOT_YEARS
    assert 475 in SNAPSHOT_YEARS
    assert 500 in SNAPSHOT_YEARS


def test_boundary_density_medieval():
    # 500 to 1500: 50-year intervals
    assert 550 in SNAPSHOT_YEARS
    assert 600 in SNAPSHOT_YEARS
    assert 1500 in SNAPSHOT_YEARS
    # should NOT have 525 (not a 50-year step from 500 in this tier)
    assert 525 not in SNAPSHOT_YEARS


def test_boundary_density_modern():
    # 1900-2026: 10-year intervals + 2026
    assert 1900 in SNAPSHOT_YEARS
    assert 1910 in SNAPSHOT_YEARS
    assert 2020 in SNAPSHOT_YEARS
    assert 2026 in SNAPSHOT_YEARS
