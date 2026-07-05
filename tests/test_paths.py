from pathlib import Path

from sovigen import paths


def test_library_dir_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path / "lib"))
    assert paths.library_dir() == tmp_path / "lib"


def test_library_dir_default(monkeypatch):
    monkeypatch.delenv("SOVIGEN_LIBRARY", raising=False)
    assert paths.library_dir() == Path("library")


def test_song_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    assert paths.song_dir("foo") == tmp_path / "foo"


def test_list_song_slugs_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path / "missing"))
    assert paths.list_song_slugs() == []


def test_list_song_slugs_sorted(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    (tmp_path / "b-song").mkdir()
    (tmp_path / "a-song").mkdir()
    (tmp_path / "note.txt").write_text("x")
    assert paths.list_song_slugs() == ["a-song", "b-song"]
