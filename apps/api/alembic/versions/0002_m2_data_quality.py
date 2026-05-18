"""m2 data quality — territory metadata, place_names, rivers, regions, capitals, timeline_notes

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-17

"""
from typing import Sequence, Union

import geoalchemy2
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, UUID

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- territories: rename confidence → confidence_type, add new columns ---
    op.alter_column("territories", "confidence", new_column_name="confidence_type")

    op.add_column("territories", sa.Column("confidence_score", sa.Float, nullable=True))
    op.add_column("territories", sa.Column("source_name", sa.Text, nullable=True))
    op.add_column("territories", sa.Column("source_url", sa.Text, nullable=True))
    op.add_column("territories", sa.Column("source_license", sa.Text, nullable=True))
    op.add_column("territories", sa.Column("data_version", sa.Text, nullable=True))
    op.add_column("territories", sa.Column("resolution_km", sa.SmallInteger, nullable=True))
    op.add_column("territories", sa.Column("importance", sa.SmallInteger, nullable=True, server_default="5"))
    op.execute("ALTER TABLE territories ADD COLUMN map_modes TEXT[] DEFAULT '{political}'")

    # --- data_sources ---
    op.create_table(
        "data_sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("url", sa.Text, nullable=True),
        sa.Column("license", sa.Text, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("year_min", sa.Integer, nullable=True),
        sa.Column("year_max", sa.Integer, nullable=True),
        sa.Column("coverage", sa.Text, nullable=True),
    )

    # --- place_names ---
    op.create_table(
        "place_names",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("name_modern", sa.Text, nullable=True),
        sa.Column("type", sa.String(50), nullable=True),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(geometry_type="POINT", srid=4326),
            nullable=False,
        ),
        sa.Column("year_start", sa.Integer, nullable=False),
        sa.Column("year_end", sa.Integer, nullable=True),
        sa.Column("min_zoom", sa.SmallInteger, nullable=True, server_default="3"),
        sa.Column("source_name", sa.Text, nullable=True),
        sa.Column("importance", sa.SmallInteger, nullable=True, server_default="5"),
        sa.Column("label_priority", sa.SmallInteger, nullable=True, server_default="5"),
    )
    op.execute("ALTER TABLE place_names ADD COLUMN map_modes TEXT[] DEFAULT '{political}'")
    op.execute("CREATE INDEX place_names_year_idx ON place_names(year_start, year_end)")
    op.execute("CREATE INDEX place_names_geom_idx ON place_names USING GIST(geom)")

    # --- rivers ---
    op.create_table(
        "rivers",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("name_alt", sa.Text, nullable=True),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(geometry_type="LINESTRING", srid=4326),
            nullable=False,
        ),
        sa.Column("year_start", sa.Integer, nullable=True),
        sa.Column("year_end", sa.Integer, nullable=True),
        sa.Column("importance", sa.SmallInteger, nullable=True, server_default="5"),
        sa.Column("source_name", sa.Text, nullable=True),
    )
    op.execute(
        "ALTER TABLE rivers ADD COLUMN map_modes TEXT[] "
        "DEFAULT '{political,physical,trade,migration,military}'"
    )
    op.execute("CREATE INDEX rivers_geom_idx ON rivers USING GIST(geom)")

    # --- entity_capitals ---
    op.create_table(
        "entity_capitals",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=False),
        sa.Column("place_name_id", UUID(as_uuid=True), nullable=False),
        sa.Column("year_start", sa.Integer, nullable=False),
        sa.Column("year_end", sa.Integer, nullable=True),
        sa.Column("capital_type", sa.String(20), nullable=True, server_default="primary"),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["place_name_id"], ["place_names.id"], ondelete="CASCADE"),
    )
    op.execute("CREATE INDEX entity_capitals_entity_idx ON entity_capitals(entity_id)")
    op.execute("CREATE INDEX entity_capitals_year_idx ON entity_capitals(year_start, year_end)")

    # --- regions ---
    op.create_table(
        "regions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("type", sa.String(30), nullable=True),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(geometry_type="MULTIPOLYGON", srid=4326),
            nullable=True,
        ),
        sa.Column("year_start", sa.Integer, nullable=True),
        sa.Column("year_end", sa.Integer, nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("source_name", sa.Text, nullable=True),
    )
    op.execute(
        "ALTER TABLE regions ADD COLUMN map_modes TEXT[] DEFAULT '{physical,cultural}'"
    )
    op.execute("CREATE INDEX regions_geom_idx ON regions USING GIST(geom)")

    # --- timeline_notes ---
    op.create_table(
        "timeline_notes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("year", sa.Integer, nullable=False),
        sa.Column("note", sa.Text, nullable=False),
        sa.Column("entity_id", UUID(as_uuid=True), nullable=True),
        sa.Column("region", sa.Text, nullable=True),
        sa.Column("importance", sa.SmallInteger, nullable=True, server_default="5"),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="SET NULL"),
    )
    op.execute("CREATE INDEX timeline_notes_year_idx ON timeline_notes(year)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS timeline_notes_year_idx")
    op.drop_table("timeline_notes")

    op.execute("DROP INDEX IF EXISTS regions_geom_idx")
    op.drop_table("regions")

    op.execute("DROP INDEX IF EXISTS entity_capitals_year_idx")
    op.execute("DROP INDEX IF EXISTS entity_capitals_entity_idx")
    op.drop_table("entity_capitals")

    op.execute("DROP INDEX IF EXISTS rivers_geom_idx")
    op.drop_table("rivers")

    op.execute("DROP INDEX IF EXISTS place_names_geom_idx")
    op.execute("DROP INDEX IF EXISTS place_names_year_idx")
    op.drop_table("place_names")
    op.drop_table("data_sources")

    op.drop_column("territories", "map_modes")
    op.drop_column("territories", "importance")
    op.drop_column("territories", "resolution_km")
    op.drop_column("territories", "data_version")
    op.drop_column("territories", "source_license")
    op.drop_column("territories", "source_url")
    op.drop_column("territories", "source_name")
    op.drop_column("territories", "confidence_score")
    op.alter_column("territories", "confidence_type", new_column_name="confidence")
