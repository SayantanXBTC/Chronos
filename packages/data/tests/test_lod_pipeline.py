"""M3-J: Tests for 3-tier LOD pipeline and vertex budget enforcement."""
from __future__ import annotations

from shapely.geometry import MultiPolygon, Polygon

from data.normalize import (
    MAX_VERTICES_LO,
    coerce_valid,
    count_vertices,
    simplify_geom_all,
    to_multipolygon,
)


def _square(size: float = 1.0, x: float = 0.0, y: float = 0.0) -> MultiPolygon:
    coords = [
        (x, y), (x + size, y), (x + size, y + size), (x, y + size), (x, y)
    ]
    return MultiPolygon([Polygon(coords)])


def _complex_polygon(n: int = 2000) -> MultiPolygon:
    """Generate polygon with ~n vertices by creating a fine-grained circle approximation."""
    import math
    coords = [
        (10.0 * math.cos(2 * math.pi * i / n), 10.0 * math.sin(2 * math.pi * i / n))
        for i in range(n)
    ]
    coords.append(coords[0])
    return MultiPolygon([Polygon(coords)])


class TestCountVertices:
    def test_simple_square_has_5_vertices(self):
        mp = _square()
        # Polygon ring: 4 corners + closing point = 5
        assert count_vertices(mp) == 5

    def test_two_polygons_vertices_summed(self):
        p1 = Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])
        p2 = Polygon([(2, 0), (3, 0), (3, 1), (2, 0)])
        mp = MultiPolygon([p1, p2])
        assert count_vertices(mp) == count_vertices(MultiPolygon([p1])) + count_vertices(MultiPolygon([p2]))

    def test_zero_vertices_empty_multipolygon(self):
        mp = MultiPolygon()
        assert count_vertices(mp) == 0


class TestSimplifyGeomAll:
    def test_returns_three_geometries(self):
        mp = _square(10.0)
        hi, med, lo = simplify_geom_all(mp)
        assert hi is not None
        assert med is not None
        assert lo is not None

    def test_hi_geom_is_unmodified_input(self):
        mp = _square(10.0)
        hi, _, _ = simplify_geom_all(mp)
        assert hi.equals(mp)

    def test_lo_has_fewer_vertices_than_hi_for_complex_geom(self):
        mp = _complex_polygon(2000)
        hi, _, lo = simplify_geom_all(mp)
        assert count_vertices(lo) < count_vertices(hi)

    def test_med_between_hi_and_lo_vertex_count(self):
        mp = _complex_polygon(2000)
        hi, med, lo = simplify_geom_all(mp)
        assert count_vertices(lo) <= count_vertices(med) <= count_vertices(hi)

    def test_lo_within_vertex_budget(self):
        mp = _complex_polygon(5000)
        _, _, lo = simplify_geom_all(mp)
        assert count_vertices(lo) <= MAX_VERTICES_LO

    def test_med_has_more_vertices_than_lo(self):
        mp = _complex_polygon(5000)
        _, med, lo = simplify_geom_all(mp)
        assert count_vertices(med) >= count_vertices(lo)

    def test_all_three_tiers_are_valid(self):
        mp = _complex_polygon(1000)
        hi, med, lo = simplify_geom_all(mp)
        assert hi.is_valid
        assert med.is_valid
        assert lo.is_valid

    def test_simple_square_not_over_simplified(self):
        mp = _square(10.0)
        hi, med, lo = simplify_geom_all(mp)
        # A simple square should survive all tiers
        assert not lo.is_empty

    def test_all_tiers_are_multipolygon_type(self):
        mp = _square(10.0)
        hi, med, lo = simplify_geom_all(mp)
        assert hi.geom_type == "MultiPolygon"
        assert med.geom_type == "MultiPolygon"
        assert lo.geom_type == "MultiPolygon"


class TestVertexBudgetConstants:
    def test_max_vertices_lo_is_positive(self):
        assert MAX_VERTICES_LO > 0

    def test_lo_budget_less_than_5000(self):
        assert MAX_VERTICES_LO < 5000

    def test_lo_budget_reasonable(self):
        # Should be between 200 and 5000
        assert 200 <= MAX_VERTICES_LO <= 5000


class TestToMultipolygon:
    def test_polygon_converted_to_multipolygon(self):
        poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 0)])
        result = to_multipolygon(poly)
        assert result.geom_type == "MultiPolygon"

    def test_multipolygon_returned_unchanged(self):
        mp = _square(5.0)
        result = to_multipolygon(mp)
        assert result.geom_type == "MultiPolygon"
        assert result.equals(mp)


class TestCoerceValid:
    def test_valid_polygon_unchanged(self):
        mp = _square(5.0)
        result = coerce_valid(mp)
        assert result.is_valid

    def test_self_intersecting_polygon_repaired(self):
        # Bowtie polygon (self-intersecting)
        bowtie = Polygon([(0, 0), (2, 2), (2, 0), (0, 2), (0, 0)])
        assert not bowtie.is_valid
        result = coerce_valid(bowtie)
        assert result.is_valid
