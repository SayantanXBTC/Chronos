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


def adaptive_tolerance(zoom_target: int) -> float:
    """Calculate Shapely simplification tolerance for a target zoom level.

    Targets ~2-pixel simplification at the given zoom, accounting for
    geographic projection (degrees per pixel at equator).
    """
    pixels_per_degree = 256 * (2 ** zoom_target) / 360
    return 2.0 / pixels_per_degree


def count_vertices(geom: MultiPolygon) -> int:
    """Count total coordinate pairs across all rings in a MultiPolygon."""
    return sum(
        len(ring.coords)
        for poly in geom.geoms
        for ring in [poly.exterior, *poly.interiors]
    )


# Zoom thresholds for LOD selection at query time
ZOOM_LO_MAX = 4   # zoom <= 4: use geom_lo
ZOOM_MED_MAX = 8  # zoom 5-8: use simplified_geom (existing)
# zoom >= 9: use geom (full resolution)

# Per-tier tolerances
TOLERANCE_HI  = adaptive_tolerance(9)   # ~0.001 degrees — full detail tier (zoom >= 9)
TOLERANCE_MED = 0.05                    # existing value — kept for backward compat
TOLERANCE_LO  = adaptive_tolerance(4)   # ~0.14 degrees — coarse world view

# Vertex budget for geom_lo — prevents massive polygons at world zoom
MAX_VERTICES_LO = 1000


def simplify_geom_lo(geom: MultiPolygon) -> MultiPolygon:
    """Produce the coarse (zoom <= 4) LOD geometry.

    Uses adaptive tolerance for zoom 4. If the result still exceeds
    MAX_VERTICES_LO vertices, iteratively doubles the tolerance until
    it fits. Preserves topology throughout.
    """
    tolerance = TOLERANCE_LO
    result = to_multipolygon(geom.simplify(tolerance, preserve_topology=True))
    while count_vertices(result) > MAX_VERTICES_LO:
        tolerance *= 2
        simplified = geom.simplify(tolerance, preserve_topology=True)
        result = to_multipolygon(simplified)
    return result


def simplify_geom_all(geom: MultiPolygon) -> tuple[MultiPolygon, MultiPolygon, MultiPolygon]:
    """Produce all three LOD tiers from a single MultiPolygon.

    Returns: (geom_hi, geom_med, geom_lo)
    - geom_hi: full resolution (returned as-is, no simplification)
    - geom_med: medium detail (zoom 5-8), tolerance=0.05
    - geom_lo: coarse (zoom <= 4), adaptive tolerance + vertex budget
    """
    geom_hi = geom  # full resolution — no simplification applied
    geom_med = simplify_geom(geom, TOLERANCE_MED)
    geom_lo = simplify_geom_lo(geom)
    return geom_hi, geom_med, geom_lo


def validate_geom(geom: BaseGeometry) -> bool:
    return bool(geom.is_valid)
