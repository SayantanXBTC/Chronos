"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "entities",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(100), unique=True, nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("color", sa.String(7), nullable=True),
    )

    op.create_table(
        "entity_names",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text, nullable=False),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("year_start", sa.Integer, nullable=False),
        sa.Column("year_end", sa.Integer, nullable=True),
        sa.Column("is_primary", sa.Boolean, nullable=False, server_default="true"),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"]),
    )

    op.create_table(
        "territories",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(geometry_type="MULTIPOLYGON", srid=4326),
            nullable=False,
        ),
        sa.Column(
            "simplified_geom",
            geoalchemy2.types.Geometry(geometry_type="MULTIPOLYGON", srid=4326),
            nullable=True,
        ),
        sa.Column("year_start", sa.Integer, nullable=False),
        sa.Column("year_end", sa.Integer, nullable=True),
        sa.Column("confidence", sa.String(20), nullable=False, server_default="approximate"),
        sa.Column("source", sa.Text, nullable=True),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"]),
    )

    op.create_table(
        "events",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(100), unique=True, nullable=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("year_start", sa.Integer, nullable=False),
        sa.Column("year_end", sa.Integer, nullable=True),
        sa.Column("magnitude", sa.SmallInteger, nullable=True),
        sa.Column("geom", geoalchemy2.types.Geometry(srid=4326), nullable=True),
        sa.Column("layer", sa.String(50), nullable=False, server_default="political"),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("description", sa.Text, nullable=True),
    )

    op.create_table(
        "event_entities",
        sa.Column("event_id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("role", sa.String(50), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"]),
    )

    op.create_table(
        "layers",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("display_name", sa.Text, nullable=False),
        sa.Column("active", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("description", sa.Text, nullable=True),
    )

    op.create_table(
        "layer_features",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("layer_id", sa.String(50), nullable=False),
        sa.Column("geom", geoalchemy2.types.Geometry(srid=4326), nullable=False),
        sa.Column("year_start", sa.Integer, nullable=False),
        sa.Column("year_end", sa.Integer, nullable=True),
        sa.Column("properties", sa.dialects.postgresql.JSONB, nullable=False, server_default="{}"),
        sa.ForeignKeyConstraint(["layer_id"], ["layers.id"]),
    )

    # Spatial indexes
    op.execute("CREATE INDEX idx_territories_geom ON territories USING GIST(geom)")
    op.execute("CREATE INDEX idx_territories_simplified ON territories USING GIST(simplified_geom)")
    op.execute("CREATE INDEX idx_layer_features_geom ON layer_features USING GIST(geom)")

    # Temporal indexes
    op.execute("CREATE INDEX idx_territories_years ON territories(year_start, year_end)")
    op.execute("CREATE INDEX idx_territories_entity_years ON territories(entity_id, year_start, year_end)")
    op.execute("CREATE INDEX idx_entity_names_years ON entity_names(year_start, year_end)")
    op.execute("CREATE INDEX idx_events_years ON events(year_start, year_end)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_events_years")
    op.execute("DROP INDEX IF EXISTS idx_entity_names_years")
    op.execute("DROP INDEX IF EXISTS idx_territories_entity_years")
    op.execute("DROP INDEX IF EXISTS idx_territories_years")
    op.execute("DROP INDEX IF EXISTS idx_layer_features_geom")
    op.execute("DROP INDEX IF EXISTS idx_territories_simplified")
    op.execute("DROP INDEX IF EXISTS idx_territories_geom")

    op.drop_table("layer_features")
    op.drop_table("layers")
    op.drop_table("event_entities")
    op.drop_table("events")
    op.drop_table("territories")
    op.drop_table("entity_names")
    op.drop_table("entities")
