import uuid

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    year_start: Mapped[int] = mapped_column(nullable=False)
    year_end: Mapped[int | None] = mapped_column(nullable=True)
    magnitude: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    geom: Mapped[bytes | None] = mapped_column(Geometry(srid=4326), nullable=True)
    layer: Mapped[str] = mapped_column(String(50), default="political")
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class EventEntity(Base):
    __tablename__ = "event_entities"

    event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("events.id"), primary_key=True
    )
    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("entities.id"), primary_key=True
    )
    role: Mapped[str | None] = mapped_column(String(50), nullable=True)
