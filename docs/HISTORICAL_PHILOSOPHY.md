# Historical Simplification Philosophy

This document defines how the platform represents historical boundaries, time, and uncertainty. All contributors must read and follow these policies before submitting territory data.

---

## 1. Border Representation Policy

**All borders are approximations** unless both `confidence_type = 'exact'` and `date_precision = 'exact'` are set. In practice, exact confidence applies only to modern borders with direct cadastral sources.

**Disputed borders**: Render the dominant scholarly consensus, not modern political claims. The platform represents historical reality as understood by academic historians, not contemporary politics. When scholarly opinion is genuinely divided, prefer the more conservative (smaller) boundary and set `confidence_type = 'approximate'`.

**Nomadic empires**: Render core territory (areas of direct administration or regular tribute collection) as the primary polygon. Maximum influence zones are a separate phase with lower confidence. Never conflate sphere of influence with administrative control.

**Maritime empires**: Render land territory only. Island possessions should be separate polygon parts within the same MultiPolygon feature, not separate phase files.

**Frontier zones**: Use the edge of documented administration, not the edge of military reach. A Roman legion march does not constitute Roman territory.

---

## 2. Temporal Approximation Policy

**Phase boundaries**: Use the documented historical event date when available (e.g., 330 CE for Constantinople's founding as capital). When no precise date is documented, use the decade midpoint and set `date_precision = 'estimated'`.

**Scholarly disagreement**: When sources differ on a date, use the median of cited academic dates. Always set `date_precision = 'estimated'` when using a median. Document the range in a commit message or source note.

**Pre-600 BCE rule**: Never assert an exact year (`date_precision = 'exact'`) for events before 600 BCE without citing a primary source with direct dating evidence. Default to `date_precision = 'estimated'` for all Bronze Age and early Iron Age events.

**End events**: All phases with a known `year_end` must include `end_event_type`. Valid values:

| Value | Meaning |
|-------|---------|
| `conquest` | External military conquest ended control |
| `collapse` | Internal collapse, civil war, or dissolution |
| `partition` | Entity split into successor states |
| `administrative_reorganization` | Continuity of state, change of form |
| `succession` | Peaceful dynastic succession |
| `absorption` | Absorbed into a larger entity |

---

## 3. Overlap Policy

**Overlapping territories at the same year are valid and expected.** Contested regions, vassal states, and zones of competing influence appear as overlapping polygons. Do not merge or clip overlapping territories at ingest — preserve raw historical reality.

The client renders overlapping polygons with Z-order by `importance` descending (higher importance entities render on top). Contributors should not attempt to resolve overlaps in the data.

**Shared coastlines and rivers**: Adjacent entities sharing a natural border will have geometrically overlapping edges due to floating-point representation. This is acceptable and expected. Do not clip to avoid it.

---

## 4. Missing Data Policy

**Prefer no territory over a fabricated territory.** An entity can exist in the `entities` table without any territory rows. This means "presence known, extent unknown" — the entity appears in the sidebar and timeline but not on the map.

Specific cases:
- **Pre-state polities**: Chiefdoms, tribal confederations, and semi-sedentary peoples with unclear territory should have `confidence_type = 'inferred'` and a low `confidence_score` (≤ 0.4).
- **Maritime/island entities**: If territorial extent is genuinely unknown, omit the territory rather than guessing.
- **Early dynastic periods**: When founding dates of entities are debated by more than 100 years, omit the uncertain early phase rather than inventing one.

---

## 5. Source Hierarchy

All territory data must have `source_license` populated. Use this priority order:

1. **Peer-reviewed academic GIS datasets** — AWMC, CHGIS, cShapes 2.0. These are directly ingestible and authoritative within their scope.
2. **Well-curated crowdsourced datasets** — OpenHistoricalMap (OHM). Good for medieval and early modern periods. Verify against secondary sources.
3. **Published historical atlases** — Manual traces from Barrington, Times Atlas of World History, or equivalent peer-reviewed atlases. Set `source_name` to the atlas title and edition.
4. **Estimated approximations** — Last resort. Use `confidence_type = 'inferred'`, `confidence_score ≤ 0.4`, and note the basis of the estimate in the source field.

**License restrictions**: Sources marked `CC BY-NC` (e.g., AWMC) prohibit commercial use of derived data. Flag these in `registry.yaml` and do not use them if this platform is ever commercialized without re-licensing.

---

## 6. Geometry Quality Standards

All submitted geometries must pass validation (`python -m data validate --all`):

- Valid GeoJSON MultiPolygon (no self-intersecting rings)
- WGS84 coordinates (lon: −180→180, lat: −90→90)
- Area > 0
- No duplicate vertices within a ring
- Minimum vertex count ≥ 4 per polygon ring
- `source_license` not null
- `date_precision` set

**Resolution guidelines**:

| Entity scale | `resolution_km` | Approx. vertices per polygon |
|-------------|----------------|------------------------------|
| City-state / small kingdom | 25–50 | 10–50 |
| Regional empire | 100–150 | 30–100 |
| Continental empire | 150–250 | 50–150 |
| Steppe / nomadic empire | 200–300 | 20–80 |

Coarser resolution is preferred for large entities. Do not submit >500-vertex polygons for entities with `resolution_km > 100` — simplify first.

---

## 7. Contribution Checklist

Before submitting a pull request with new or modified territory data:

- [ ] `python -m data validate --all` passes with 0 errors
- [ ] All new phases have `date_precision`, `confidence_type`, `confidence_score`, `source_name`, `source_license`
- [ ] All phases with a known `year_end` have `end_event_type`
- [ ] Entity has a `type` from the taxonomy (`empire`, `dynasty`, `kingdom`, `republic`, `caliphate`, `sultanate`, `nomadic_empire`, `city_state`, `tribe`, `colony`, `other`)
- [ ] Lineage relationships declared in `data/raw/lineages/all.yaml` where applicable
- [ ] `resolution_km` set appropriately for entity scale
- [ ] Generator script committed to `scripts/` if geometry was programmatically created
- [ ] Commit message names the source (e.g., `feat(data): Han Dynasty — CHGIS v6 traces`)
