from shapely.geometry import GeometryCollection, MultiPolygon, Polygon
from shapely.geometry.base import BaseGeometry
from shapely.validation import make_valid


def to_multipolygon(geom: BaseGeometry) -> MultiPolygon:
    if isinstance(geom, MultiPolygon):
        return geom
    if isinstance(geom, Polygon):
        return MultiPolygon([geom])
    raise ValueError(f"Cannot convert {geom.geom_type} to MultiPolygon")


def coerce_valid(geom: BaseGeometry) -> BaseGeometry:
    """Return a topologically valid Polygon or MultiPolygon.

    Approximate bounding-box polygons frequently share border points or
    overlap slightly.  ``make_valid`` fixes ring self-intersections and
    overlapping component polygons while preserving the covered area.
    When ``make_valid`` returns a ``GeometryCollection`` (mixed types),
    only the polygon parts are retained and merged into a MultiPolygon.
    """
    if geom.is_valid:
        return geom
    fixed = make_valid(geom)
    if isinstance(fixed, GeometryCollection) and not isinstance(
        fixed, (Polygon, MultiPolygon)
    ):
        polys = [g for g in fixed.geoms if isinstance(g, (Polygon, MultiPolygon))]
        if not polys:
            return fixed
        parts: list[Polygon] = []
        for p in polys:
            if isinstance(p, Polygon):
                parts.append(p)
            else:
                parts.extend(p.geoms)
        fixed = MultiPolygon(parts)
    return fixed


def simplify_geom(geom: MultiPolygon, tolerance: float = 0.05) -> MultiPolygon:
    simplified = geom.simplify(tolerance, preserve_topology=True)
    return to_multipolygon(simplified)


def validate_geom(geom: BaseGeometry) -> bool:
    return bool(geom.is_valid)
