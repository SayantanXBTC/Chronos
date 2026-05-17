import pytest
from data.normalize import fix_geometry, simplify_geometry, to_multipolygon


def test_polygon_becomes_multipolygon():
    polygon = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]}
    result = to_multipolygon(polygon)
    assert result["type"] == "MultiPolygon"


def test_multipolygon_unchanged():
    mp = {"type": "MultiPolygon", "coordinates": [[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]]}
    result = to_multipolygon(mp)
    assert result["type"] == "MultiPolygon"


def test_unsupported_type_raises():
    point = {"type": "Point", "coordinates": [0, 0]}
    with pytest.raises(ValueError, match="Expected Polygon or MultiPolygon"):
        to_multipolygon(point)


def test_fix_geometry_returns_multipolygon():
    # Self-intersecting "bowtie" polygon — Shapely can repair it
    bowtie = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [1, 1], [1, 0], [0, 1], [0, 0]]],
    }
    result = fix_geometry(bowtie)
    assert result["type"] == "MultiPolygon"


def test_simplify_returns_multipolygon():
    mp = {"type": "MultiPolygon", "coordinates": [[[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]]}
    result = simplify_geometry(mp, tolerance=0.01)
    assert result["type"] == "MultiPolygon"


def test_simplify_reduces_coordinates():
    # A polygon with many points should have fewer after simplification
    coords = [[[i * 0.001, 0] for i in range(100)] + [[0.1, 0.1], [0, 0]]]
    mp = {"type": "MultiPolygon", "coordinates": [coords]}
    result = simplify_geometry(mp, tolerance=0.01)
    result_coords = result["coordinates"][0][0]
    assert len(result_coords) < 100
