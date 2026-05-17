import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.database import Base


async def test_all_tables_registered():
    """All required tables are registered in Base.metadata."""
    import app.models  # noqa: F401
    table_names = set(Base.metadata.tables.keys())
    required = {
        "entities", "entity_names", "territories",
        "events", "event_entities", "layers", "layer_features"
    }
    assert required.issubset(table_names), f"Missing tables: {required - table_names}"


async def test_entity_table_columns():
    """Entity table has required columns."""
    import app.models  # noqa: F401
    table = Base.metadata.tables["entities"]
    col_names = {c.name for c in table.columns}
    assert {"id", "slug", "type", "color"}.issubset(col_names)


async def test_territory_table_columns():
    """Territory table has required columns including temporal bounds."""
    import app.models  # noqa: F401
    table = Base.metadata.tables["territories"]
    col_names = {c.name for c in table.columns}
    assert {"id", "entity_id", "year_start", "year_end", "confidence", "source"}.issubset(col_names)


async def test_event_table_columns():
    """Event table has required columns."""
    import app.models  # noqa: F401
    table = Base.metadata.tables["events"]
    col_names = {c.name for c in table.columns}
    assert {"id", "type", "year_start", "year_end", "magnitude", "title", "layer"}.issubset(col_names)


async def test_entity_names_temporal_columns():
    """EntityName table has temporal range columns."""
    import app.models  # noqa: F401
    table = Base.metadata.tables["entity_names"]
    col_names = {c.name for c in table.columns}
    assert {"entity_id", "name", "year_start", "year_end", "is_primary"}.issubset(col_names)
