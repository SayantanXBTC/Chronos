from data.entity_map import resolve_slug


def test_resolve_roman_empire():
    assert resolve_slug("Roman Empire") == "roman-empire"


def test_resolve_roman_republic():
    assert resolve_slug("Roman Republic") == "roman-empire"


def test_resolve_han_dynasty():
    assert resolve_slug("Han Dynasty") == "han-dynasty"


def test_resolve_unknown_returns_none():
    assert resolve_slug("Unknown Polity XYZ") is None


def test_resolve_case_sensitive():
    # Map is exact-match, not case-insensitive
    assert resolve_slug("roman empire") is None
