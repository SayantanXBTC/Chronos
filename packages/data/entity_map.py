ENTITY_SLUG_MAP: dict[str, str] = {
    "Roman Empire": "roman-empire",
    "Roman Republic": "roman-empire",
    "Roma": "roman-empire",
    "ROMAN_EMP": "roman-empire",
    "Rome": "roman-empire",
    "Han Dynasty": "han-dynasty",
    "Han China": "han-dynasty",
    "HAN": "han-dynasty",
    "Han": "han-dynasty",
}


def resolve_slug(source_name: str) -> str | None:
    """Return canonical entity slug for source_name, or None if unmapped."""
    return ENTITY_SLUG_MAP.get(source_name)
