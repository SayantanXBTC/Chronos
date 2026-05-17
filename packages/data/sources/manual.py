"""
MVP seed data for Rome and Han Dynasty.
Geometries are simplified approximations for proof-of-concept only.
"""
from data.sources.base import EntityRecord, SourceParser, TerritoryRecord

ENTITIES = [
    EntityRecord(
        slug="roman-empire",
        type="empire",
        color="#C0392B",
        names=[
            {
                "name": "Roman Republic",
                "language": "en",
                "year_start": -509,
                "year_end": -27,
                "is_primary": True,
            },
            {
                "name": "Roman Empire",
                "language": "en",
                "year_start": -27,
                "year_end": 476,
                "is_primary": True,
            },
        ],
    ),
    EntityRecord(
        slug="han-dynasty",
        type="empire",
        color="#E67E22",
        names=[
            {
                "name": "Han Dynasty",
                "language": "en",
                "year_start": -206,
                "year_end": 220,
                "is_primary": True,
            }
        ],
    ),
]

TERRITORIES = [
    TerritoryRecord(
        entity_slug="roman-empire",
        geojson={
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [-10.0, 30.0],
                        [40.0, 30.0],
                        [45.0, 42.0],
                        [35.0, 47.0],
                        [15.0, 50.0],
                        [-5.0, 44.0],
                        [-10.0, 36.0],
                        [-10.0, 30.0],
                    ]
                ]
            ],
        },
        year_start=-264,
        year_end=476,
        confidence="approximate",
        source="manual-mvp",
    ),
    TerritoryRecord(
        entity_slug="han-dynasty",
        geojson={
            "type": "MultiPolygon",
            "coordinates": [
                [
                    [
                        [100.0, 20.0],
                        [135.0, 20.0],
                        [135.0, 45.0],
                        [120.0, 52.0],
                        [100.0, 50.0],
                        [95.0, 35.0],
                        [100.0, 20.0],
                    ]
                ]
            ],
        },
        year_start=-206,
        year_end=220,
        confidence="approximate",
        source="manual-mvp",
    ),
]


class ManualSource(SourceParser):
    def get_entities(self) -> list[EntityRecord]:
        return ENTITIES

    def get_territories(self) -> list[TerritoryRecord]:
        return TERRITORIES
