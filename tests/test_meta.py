import pytest

from sovigen import meta


def test_new_meta_shape():
    data = meta.new_meta("My Song", "my-song", "2026-06-22")
    assert data == {
        "title": "My Song",
        "slug": "my-song",
        "stage": "draft",
        "created": "2026-06-22",
    }


def test_write_then_read_roundtrip(tmp_path):
    data = meta.new_meta("Привет", "privet", "2026-06-22")
    meta.write_meta(tmp_path, data)
    assert meta.read_meta(tmp_path) == data


def test_write_preserves_cyrillic_unescaped(tmp_path):
    meta.write_meta(tmp_path, meta.new_meta("Привет", "privet", "2026-06-22"))
    text = (tmp_path / "meta.json").read_text(encoding="utf-8")
    assert "Привет" in text


def test_has_meta(tmp_path):
    assert meta.has_meta(tmp_path) is False
    meta.write_meta(tmp_path, meta.new_meta("X", "x", "2026-06-22"))
    assert meta.has_meta(tmp_path) is True


def test_set_stage_valid(tmp_path):
    meta.write_meta(tmp_path, meta.new_meta("X", "x", "2026-06-22"))
    meta.set_stage(tmp_path, "ready")
    assert meta.read_meta(tmp_path)["stage"] == "ready"


def test_set_stage_invalid(tmp_path):
    meta.write_meta(tmp_path, meta.new_meta("X", "x", "2026-06-22"))
    with pytest.raises(ValueError):
        meta.set_stage(tmp_path, "bogus")
