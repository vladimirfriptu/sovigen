import json

import pytest

from sovigen import meta


def test_new_meta_shape():
    data = meta.new_meta("My Song", "my-song", "2026-07-30")
    assert data == {
        "meta_version": 2,
        "title": "My Song",
        "slug": "my-song",
        "stage": "idea",
        "created": "2026-07-30",
        "source": None,
        "series": None,
        "language": "uk",
        "style": None,
        "suno_takes": 0,
        "stage_history": [{"stage": "idea", "at": "2026-07-30"}],
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


def test_read_normalizes_v1_draft_to_idea(tmp_path):
    legacy = {"title": "X", "slug": "x", "stage": "draft", "created": "2026-06-22"}
    (tmp_path / "meta.json").write_text(json.dumps(legacy), encoding="utf-8")
    data = meta.read_meta(tmp_path)
    assert data["stage"] == "idea"
    assert data["meta_version"] == 2
    assert data["stage_history"] == []


def test_read_keeps_v1_published_stage(tmp_path):
    legacy = {"title": "X", "slug": "x", "stage": "published", "created": "2026-06-22"}
    (tmp_path / "meta.json").write_text(json.dumps(legacy), encoding="utf-8")
    assert meta.read_meta(tmp_path)["stage"] == "published"


def test_read_does_not_rewrite_file(tmp_path):
    legacy = {"title": "X", "slug": "x", "stage": "draft", "created": "2026-06-22"}
    path = tmp_path / "meta.json"
    path.write_text(json.dumps(legacy), encoding="utf-8")
    meta.read_meta(tmp_path)
    assert json.loads(path.read_text(encoding="utf-8")) == legacy


def test_set_stage_appends_history(tmp_path):
    meta.write_meta(tmp_path, meta.new_meta("X", "x", "2026-07-30"))
    meta.set_stage(tmp_path, "brief", "2026-07-31")
    data = meta.read_meta(tmp_path)
    assert data["stage"] == "brief"
    assert data["stage_history"][-1] == {"stage": "brief", "at": "2026-07-31"}


def test_set_stage_invalid(tmp_path):
    meta.write_meta(tmp_path, meta.new_meta("X", "x", "2026-07-30"))
    with pytest.raises(ValueError):
        meta.set_stage(tmp_path, "bogus", "2026-07-31")


def test_next_stage():
    assert meta.next_stage("idea") == "brief"
    assert meta.next_stage("ready") == "pre-published"
    assert meta.next_stage("published") is None


def test_next_stage_unknown_returns_none(tmp_path):
    assert meta.next_stage("mastering") is None
    assert meta.next_stage("") is None


def test_write_is_atomic_on_failure(tmp_path, monkeypatch):
    original = meta.new_meta("X", "x", "2026-07-30")
    meta.write_meta(tmp_path, original)

    def boom(src, dst):
        raise OSError("no space left on device")

    monkeypatch.setattr(meta.os, "replace", boom)
    with pytest.raises(OSError):
        meta.write_meta(tmp_path, {**original, "stage": "brief"})
    assert meta.read_meta(tmp_path) == original
    assert list(tmp_path.glob(".meta-*")) == []


def test_write_leaves_no_zero_byte_meta(tmp_path):
    meta.write_meta(tmp_path, meta.new_meta("X", "x", "2026-07-30"))
    meta.write_meta(tmp_path, meta.new_meta("Y", "y", "2026-07-30"))
    assert (tmp_path / "meta.json").stat().st_size > 0
    assert list(tmp_path.glob(".meta-*")) == []
