import pytest
from shapely.geometry import Polygon, MultiPolygon, Point
from shapely import wkt as shapely_wkt

from data.normalize import to_multipolygon, simplify_geom, validate_geom, coerce_valid


def test_polygon_wraps_to_multipolygon():
    poly = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
    result = to_multipolygon(poly)
    assert isinstance(result, MultiPolygon)
    assert len(list(result.geoms)) == 1


def test_multipolygon_passthrough():
    mp = MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])])
    result = to_multipolygon(mp)
    assert result is mp


def test_non_polygon_raises():
    with pytest.raises(ValueError, match="Cannot convert"):
        to_multipolygon(Point(0, 0))


def test_simplify_returns_multipolygon():
    mp = MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])])
    result = simplify_geom(mp, tolerance=0.01)
    assert isinstance(result, MultiPolygon)


def test_simplify_reduces_vertices():
    coords = [(i * 0.001, 0.001 * (i % 3)) for i in range(200)]
    coords += [(0.2, 0.1), (0, 0.1), (0, 0)]
    poly = MultiPolygon([Polygon(coords)])
    simplified = simplify_geom(poly, tolerance=0.05)
    original_verts = sum(len(list(g.exterior.coords)) for g in poly.geoms)
    simplified_verts = sum(len(list(g.exterior.coords)) for g in simplified.geoms)
    assert simplified_verts < original_verts


def test_valid_geometry_returns_true():
    mp = MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])])
    assert validate_geom(mp) is True


def test_invalid_geometry_returns_false():
    # Self-intersecting (bowtie) polygon is invalid
    invalid = shapely_wkt.loads("POLYGON((0 0, 1 1, 1 0, 0 1, 0 0))")
    assert validate_geom(invalid) is False


def test_coerce_valid_passthrough_valid():
    mp = MultiPolygon([Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])])
    result = coerce_valid(mp)
    assert result is mp


def test_coerce_valid_fixes_overlapping_multipolygon():
    # Two overlapping squares — invalid MultiPolygon, valid after coerce
    p1 = Polygon([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)])
    p2 = Polygon([(1, 0), (3, 0), (3, 2), (1, 2), (1, 0)])
    invalid_mp = MultiPolygon([p1, p2])
    assert not invalid_mp.is_valid
    result = coerce_valid(invalid_mp)
    assert result.is_valid
    assert result.area <= p1.area + p2.area


def test_coerce_valid_returns_multipolygon():
    p1 = Polygon([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)])
    p2 = Polygon([(1, 0), (3, 0), (3, 2), (1, 2), (1, 0)])
    invalid_mp = MultiPolygon([p1, p2])
    result = coerce_valid(invalid_mp)
    assert isinstance(result, MultiPolygon)
