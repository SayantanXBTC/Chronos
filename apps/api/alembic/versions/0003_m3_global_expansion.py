"""m3 global expansion — lineages, LOD geometry, temporal uncertainty, taxonomy

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-18

"""
from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Step 1: Remap entity types before adding CHECK constraint ---
    op.execute("UPDATE entities SET type = 'empire' WHERE slug = 'roman-empire'")
    op.execute("UPDATE entities SET type = 'republic' WHERE slug = 'roman-republic'")
    op.execute("UPDATE entities SET type = 'empire' WHERE slug = 'eastern-roman-empire'")
    op.execute("UPDATE entities SET type = 'empire' WHERE slug = 'western-roman-empire'")
    op.execute("UPDATE entities SET type = 'empire' WHERE slug = 'macedonian-empire'")
    op.execute("UPDATE entities SET type = 'kingdom' WHERE slug = 'ptolemaic-egypt'")
    op.execute("UPDATE entities SET type = 'empire' WHERE slug = 'seleucid-empire'")
    op.execute("UPDATE entities SET type = 'empire' WHERE slug = 'achaemenid-persia'")
    op.execute("UPDATE entities SET type = 'empire' WHERE slug = 'parthian-empire'")
    op.execute("UPDATE entities SET type = 'republic' WHERE slug = 'carthage'")
    op.execute("UPDATE entities SET type = 'confederation' WHERE slug = 'greek-city-states'")
    op.execute("UPDATE entities SET type = 'tribal_confederation' WHERE slug = 'germanic-tribes'")
    op.execute("UPDATE entities SET type = 'kingdom' WHERE slug = 'numidia'")

    # --- Step 2: Add CHECK constraint to entities.type ---
    op.execute(
        "ALTER TABLE entities ADD CONSTRAINT entities_type_check "
        "CHECK (type IN ("
        "'empire','kingdom','republic','dynasty','caliphate','sultanate',"
        "'tribal_confederation','nomadic_empire','city_state','colony',"
        "'protectorate','confederation'"
        "))"
    )

    # --- Step 3: Add columns to territories ---
    op.execute(
        "ALTER TABLE territories ADD COLUMN geom_lo "
        "geometry(MultiPolygon, 4326)"
    )
    op.execute(
        "ALTER TABLE territories ADD COLUMN date_precision TEXT NOT NULL DEFAULT 'approximate' "
        "CHECK (date_precision IN ('exact', 'approximate', 'estimated'))"
    )
    op.execute(
        "ALTER TABLE territories ADD COLUMN end_event_type TEXT "
        "CHECK (end_event_type IN ("
        "'conquest','collapse','annexation','rebellion',"
        "'unification','succession','treaty','partition',"
        "'administrative_reorganization'"
        "))"
    )

    # --- Step 4: Create entity_lineages table ---
    op.create_table(
        "entity_lineages",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("parent_entity_id", UUID(as_uuid=True), nullable=False),
        sa.Column("child_entity_id", UUID(as_uuid=True), nullable=False),
        sa.Column("relationship_type", sa.Text, nullable=False),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.ForeignKeyConstraint(["parent_entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["child_entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("parent_entity_id", "child_entity_id", "relationship_type"),
    )
    op.execute(
        "ALTER TABLE entity_lineages ADD CONSTRAINT entity_lineages_relationship_type_check "
        "CHECK (relationship_type IN ("
        "'evolved_into','successor','continuation','split_from','merged_into'"
        "))"
    )
    op.execute("CREATE INDEX entity_lineages_parent_idx ON entity_lineages(parent_entity_id)")
    op.execute("CREATE INDEX entity_lineages_child_idx ON entity_lineages(child_entity_id)")

    # --- Step 5: Create territory_sources table (schema stub, no data) ---
    op.create_table(
        "territory_sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("territory_id", UUID(as_uuid=True), nullable=False),
        sa.Column("source_name", sa.Text, nullable=False),
        sa.Column("source_url", sa.Text, nullable=True),
        sa.Column("source_license", sa.Text, nullable=False),
        sa.Column("contribution", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["territory_id"], ["territories.id"], ondelete="CASCADE"),
    )
    op.execute(
        "CREATE INDEX territory_sources_territory_idx ON territory_sources(territory_id)"
    )

    # --- Step 6: Create region_coverage table ---
    op.create_table(
        "region_coverage",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("region_name", sa.Text, nullable=False),
        sa.Column("year_start", sa.Integer, nullable=False),
        sa.Column("year_end", sa.Integer, nullable=True),
        sa.Column(
            "completeness", sa.Text, nullable=False, server_default="none",
        ),
        sa.CheckConstraint(
            "completeness IN ('complete','partial','sparse','none')",
            name="region_coverage_completeness_check",
        ),
        sa.Column("entity_count", sa.Integer, nullable=True, server_default="0"),
        sa.Column("primary_source", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
    )

    # --- Step 7: Add columns to place_names ---
    op.add_column("place_names", sa.Column("name_local", sa.Text, nullable=True))
    op.execute(
        "ALTER TABLE place_names ADD COLUMN date_precision TEXT NOT NULL DEFAULT 'approximate' "
        "CHECK (date_precision IN ('exact', 'approximate', 'estimated'))"
    )

    # --- Step 8: Add indexes ---
    op.execute(
        "CREATE INDEX IF NOT EXISTS territories_geom_gist ON territories USING GIST(geom)"
    )
    op.execute(
        "CREATE INDEX territories_geom_lo_gist ON territories USING GIST(geom_lo)"
    )
    op.execute(
        "CREATE INDEX territories_year_start_end_idx ON territories(year_start, year_end) "
        "WHERE year_end IS NOT NULL"
    )
    op.execute(
        "CREATE INDEX place_names_importance_idx ON place_names(importance)"
    )


def downgrade() -> None:
    # --- Reverse Step 8: Drop indexes ---
    op.execute("DROP INDEX IF EXISTS place_names_importance_idx")
    op.execute("DROP INDEX IF EXISTS territories_year_start_end_idx")
    op.execute("DROP INDEX IF EXISTS territories_geom_lo_gist")
    op.execute("DROP INDEX IF EXISTS territories_geom_gist")

    # --- Reverse Step 7: Drop columns from place_names ---
    op.execute("ALTER TABLE place_names DROP COLUMN IF EXISTS date_precision")
    op.drop_column("place_names", "name_local")

    # --- Reverse Step 6: Drop region_coverage ---
    op.drop_table("region_coverage")

    # --- Reverse Step 5: Drop territory_sources ---
    op.execute("DROP INDEX IF EXISTS territory_sources_territory_idx")
    op.drop_table("territory_sources")

    # --- Reverse Step 4: Drop entity_lineages ---
    op.execute("DROP INDEX IF EXISTS entity_lineages_child_idx")
    op.execute("DROP INDEX IF EXISTS entity_lineages_parent_idx")
    op.drop_table("entity_lineages")

    # --- Reverse Step 3: Drop columns from territories ---
    op.execute("ALTER TABLE territories DROP COLUMN IF EXISTS end_event_type")
    op.execute("ALTER TABLE territories DROP COLUMN IF EXISTS date_precision")
    op.execute("ALTER TABLE territories DROP COLUMN IF EXISTS geom_lo")

    # --- Reverse Step 2: Drop CHECK constraint from entities ---
    op.execute("ALTER TABLE entities DROP CONSTRAINT IF EXISTS entities_type_check")

    # --- Reverse Step 1: Remap entity types back to 'polity' ---
    # NOTE: The entity type rollback below assumes all 13 entities had type='polity'
    # before migration 0003 ran. This was the state after migration 0002 (all entities
    # were seeded with type='polity'). If your DB diverged from that state, roll back
    # entity types manually before running this downgrade.
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'roman-empire'")
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'roman-republic'")
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'eastern-roman-empire'")
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'western-roman-empire'")
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'macedonian-empire'")
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'ptolemaic-egypt'")
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'seleucid-empire'")
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'achaemenid-persia'")
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'parthian-empire'")
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'carthage'")
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'greek-city-states'")
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'germanic-tribes'")
    op.execute("UPDATE entities SET type = 'polity' WHERE slug = 'numidia'")
