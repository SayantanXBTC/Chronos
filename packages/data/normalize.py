from shapely.geometry import mapping, shape
from shapely.validation import make_valid


def to_multipolygon(geojson: dict) -> dict:
    """Convert Polygon to MultiPolygon. Pass through MultiPolygon unchanged."""
    geom = shape(geojson)
    if geom.geom_type == "Polygon":
        from shapely.geometry import MultiPolygon
        geom = MultiPolygon([geom])
    elif geom.geom_type != "MultiPolygon":
        raise ValueError(f"Expected Polygon or MultiPolygon, got {geom.geom_type}")
    return mapping(geom)


def fix_geometry(geojson: dict) -> dict:
    """Repair invalid geometry, return as MultiPolygon."""
    geom = make_valid(shape(geojson))
    return to_multipolygon(mapping(geom))


def simplify_geometry(geojson: dict, tolerance: float = 0.1) -> dict:
    """Simplify geometry for low-zoom rendering. Returns MultiPolygon."""
    geom = shape(geojson).simplify(tolerance, preserve_topology=True)
    return to_multipolygon(mapping(geom))
