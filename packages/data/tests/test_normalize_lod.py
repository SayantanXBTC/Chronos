import pytest
from shapely.geometry import MultiPolygon, Polygon
from data.normalize import (
    adaptive_tolerance,
    count_vertices,
    simplify_geom_all,
    simplify_geom_lo,
    TOLERANCE_LO,
    TOLERANCE_MED,
    MAX_VERTICES_LO,
    ZOOM_LO_MAX,
    ZOOM_MED_MAX,
)


def make_circle_poly(center_lon: float, center_lat: float, radius: float, n: int = 200) -> MultiPolygon:
    """Create a MultiPolygon approximating a circle with n vertices — useful for LOD tests."""
    import math
    coords = [
        (center_lon + radius * math.cos(2 * math.pi * i / n),
         center_lat + radius * math.sin(2 * math.pi * i / n))
        for i in range(n)
    ]
    coords.append(coords[0])
    return MultiPolygon([Polygon(coords)])


def test_adaptive_tolerance_decreases_with_zoom():
    """Higher zoom → finer tolerance (smaller value)."""
    assert adaptive_tolerance(9) < adaptive_tolerance(4)
    assert adaptive_tolerance(4) < adaptive_tolerance(0)


def test_adaptive_tolerance_positive():
    for zoom in [0, 2, 4, 6, 9, 12]:
        assert adaptive_tolerance(zoom) > 0


def test_count_vertices_simple():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
    mp = MultiPolygon([poly])
    assert count_vertices(mp) == 5


def test_count_vertices_two_polys():
    p1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
    p2 = Polygon([(2, 0), (3, 0), (3, 1), (2, 1), (2, 0)])
    mp = MultiPolygon([p1, p2])
    assert count_vertices(mp) == 10


def test_simplify_geom_all_returns_tuple():
    mp = make_circle_poly(12.5, 41.9, 1.0, n=100)
    result = simplify_geom_all(mp)
    assert len(result) == 3


def test_simplify_geom_all_hi_is_original():
    """geom_hi should be the input geometry unchanged."""
    mp = make_circle_poly(12.5, 41.9, 1.0, n=100)
    hi, med, lo = simplify_geom_all(mp)
    assert hi is mp  # same object


def test_simplify_geom_all_lo_has_fewer_vertices():
    mp = make_circle_poly(12.5, 41.9, 1.0, n=300)
    hi, med, lo = simplify_geom_all(mp)
    assert count_vertices(lo) < count_vertices(hi)


def test_simplify_geom_all_med_has_fewer_vertices_than_hi():
    mp = make_circle_poly(12.5, 41.9, 1.0, n=300)
    hi, med, lo = simplify_geom_all(mp)
    assert count_vertices(med) < count_vertices(hi)


def test_simplify_geom_lo_respects_vertex_budget():
    """A very complex polygon (2000 vertices) should be simplified within budget."""
    mp = make_circle_poly(12.5, 41.9, 1.0, n=2000)
    lo = simplify_geom_lo(mp)
    assert count_vertices(lo) <= MAX_VERTICES_LO


def test_simplify_geom_lo_valid_geometry():
    mp = make_circle_poly(12.5, 41.9, 1.0, n=500)
    lo = simplify_geom_lo(mp)
    assert lo.is_valid


def test_tolerance_lo_less_than_med():
    """Lower zoom (lo) has coarser tolerance than med."""
    # TOLERANCE_LO is for zoom 4, TOLERANCE_MED is for zoom ~6-7
    # Both are static constants
    assert TOLERANCE_LO > TOLERANCE_MED  # larger value = coarser simplification


def test_zoom_constants():
    assert ZOOM_LO_MAX == 4
    assert ZOOM_MED_MAX == 8
