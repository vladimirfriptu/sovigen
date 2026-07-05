from sovigen.slug import slugify


def test_basic_spaces_and_case():
    assert slugify("My Track Name") == "my-track-name"


def test_trims_and_collapses_punctuation():
    assert slugify("  Hello,   World!!  ") == "hello-world"


def test_keeps_cyrillic():
    assert slugify("Привет Мир") == "привет-мир"


def test_underscores_become_hyphens():
    assert slugify("a_b__c") == "a-b-c"


def test_symbols_only_yields_empty():
    assert slugify("!!! ???") == ""
