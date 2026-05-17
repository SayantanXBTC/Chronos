import uuid

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Territory(Base):
    __tablename__ = "territories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("entities.id"), nullable=False
    )
    geom: Mapped[bytes] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=False
    )
    simplified_geom: Mapped[bytes | None] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True
    )
    year_start: Mapped[int] = mapped_column(nullable=False)
    year_end: Mapped[int | None] = mapped_column(nullable=True)
    confidence: Mapped[str] = mapped_column(String(20), default="approximate")
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
