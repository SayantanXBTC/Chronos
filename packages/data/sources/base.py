from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TerritoryRecord:
    entity_slug: str
    geojson: dict
    year_start: int
    year_end: int | None
    confidence: str = "approximate"
    source: str = "manual"


@dataclass
class EntityRecord:
    slug: str
    type: str
    color: str
    names: list[dict]


class SourceParser(ABC):
    @abstractmethod
    def get_entities(self) -> list[EntityRecord]: ...

    @abstractmethod
    def get_territories(self) -> list[TerritoryRecord]: ...
