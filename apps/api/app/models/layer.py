import uuid

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Layer(Base):
    __tablename__ = "layers"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)


class LayerFeature(Base):
    __tablename__ = "layer_features"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    layer_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("layers.id"), nullable=False
    )
    geom: Mapped[bytes] = mapped_column(Geometry(srid=4326), nullable=False)
    year_start: Mapped[int] = mapped_column(nullable=False)
    year_end: Mapped[int | None] = mapped_column(nullable=True)
    properties: Mapped[dict] = mapped_column(JSONB, default=dict)
