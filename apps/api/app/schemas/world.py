from typing import Any
from pydantic import BaseModel


class WorldStateResponse(BaseModel):
    type: str = "FeatureCollection"
    year: int
    snapshot_year: int
    features: list[dict[str, Any]]
