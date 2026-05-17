from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry


def to_multipolygon(geom: BaseGeometry) -> MultiPolygon:
    if isinstance(geom, MultiPolygon):
        return geom
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    raise ValueError(f"Cannot convert {geom.geom_type} to MultiPolygon")


def simplify_geom(geom: MultiPolygon, tolerance: float = 0.05) -> MultiPolygon:
    simplified = geom.simplify(tolerance, preserve_topology=True)
    return to_multipolygon(simplified)


def validate_geom(geom: BaseGeometry) -> bool:
    return bool(geom.is_valid)
