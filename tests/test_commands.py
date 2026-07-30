import subprocess

import pytest

from sovigen import commands, meta


@pytest.fixture
def lib(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path / "library"))
    return tmp_path / "library"


def _make_song(lib, slug, stage="idea", with_inputs=True):
    sdir = lib / slug
    (sdir / "raw").mkdir(parents=True)
    meta.write_meta(sdir, meta.new_meta(slug, slug, "2026-06-22"))
    if stage != "idea":
        meta.set_stage(sdir, stage, "2026-06-22")
    if with_inputs:
        (sdir / "cover.png").write_bytes(b"")
        (sdir / "track.mp3").write_bytes(b"")
    return sdir


def _fake_ffmpeg_ok(monkeypatch):
    def fake_run(cmd, capture_output=True, text=True):
        output = cmd[-1]
        open(output, "wb").close()

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)


def test_new_creates_structure(lib):
    sdir = commands.cmd_new("Мій щит")
    assert (sdir / "raw").is_dir()
    assert (sdir / "meta.json").is_file()
    data = meta.read_meta(sdir)
    assert data["stage"] == "idea"
    assert data["meta_version"] == 2


def test_new_renders_artifacts(lib):
    sdir = commands.cmd_new("Мій щит")
    for name in ["brief.md", "lyrics.md", "suno.md", "cover-prompt.md",
                 "youtube.md", "notes.md"]:
        assert (sdir / name).is_file(), name


def test_new_records_source_and_series(lib):
    sdir = commands.cmd_new("Мій щит", source="psalm-3", series="psalms")
    data = meta.read_meta(sdir)
    assert data["source"] == "psalm-3"
    assert data["series"] == "psalms"
    assert "source: psalm-3" in (sdir / "brief.md").read_text(encoding="utf-8")


def test_new_rejects_existing(lib):
    commands.cmd_new("Dup")
    with pytest.raises(commands.CommandError):
        commands.cmd_new("Dup")


def test_new_rejects_empty_slug(lib):
    with pytest.raises(commands.CommandError):
        commands.cmd_new("!!!")


def test_build_happy_path(lib, monkeypatch):
    _make_song(lib, "song-a", stage="ready")
    _fake_ffmpeg_ok(monkeypatch)
    out = commands.cmd_build("song-a")
    assert out.exists()
    assert out.name == "youtube.mp4"
    assert meta.read_meta(lib / "song-a")["stage"] == "pre-published"


def test_build_unknown_slug(lib):
    with pytest.raises(commands.CommandError):
        commands.cmd_build("nope")


def test_build_refuses_existing_output(lib, monkeypatch):
    sdir = _make_song(lib, "song-b", stage="ready")
    (sdir / "youtube.mp4").write_bytes(b"")
    _fake_ffmpeg_ok(monkeypatch)
    with pytest.raises(commands.CommandError):
        commands.cmd_build("song-b")


def test_build_ffmpeg_failure_keeps_stage(lib, monkeypatch):
    _make_song(lib, "song-c", stage="ready")

    def fake_run(cmd, capture_output=True, text=True):
        class R:
            returncode = 1
            stderr = "boom"

        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(commands.CommandError):
        commands.cmd_build("song-c")
    assert meta.read_meta(lib / "song-c")["stage"] == "ready"


def test_build_all_only_ready(lib, monkeypatch):
    _make_song(lib, "ready-one", stage="ready")
    _make_song(lib, "draft-one", stage="draft")
    _fake_ffmpeg_ok(monkeypatch)
    built = commands.cmd_build_all()
    assert built == ["ready-one"]
    assert meta.read_meta(lib / "ready-one")["stage"] == "pre-published"
    assert meta.read_meta(lib / "draft-one")["stage"] == "draft"


def test_build_all_skips_dirs_without_meta(lib, monkeypatch):
    (lib / "junk").mkdir(parents=True)
    _fake_ffmpeg_ok(monkeypatch)
    assert commands.cmd_build_all() == []


def test_ready_sets_stage(lib):
    _make_song(lib, "song-r", stage="draft")
    commands.cmd_ready("song-r")
    assert meta.read_meta(lib / "song-r")["stage"] == "ready"


def test_ready_unknown_slug(lib):
    with pytest.raises(commands.CommandError):
        commands.cmd_ready("nope")


def test_publish_sets_stage(lib):
    _make_song(lib, "song-d", stage="pre-published")
    commands.cmd_publish("song-d")
    assert meta.read_meta(lib / "song-d")["stage"] == "published"


def test_status_lists_rows(lib):
    _make_song(lib, "song-e", stage="ready")
    rows = commands.cmd_status()
    assert {"slug": "song-e", "stage": "ready", "title": "song-e"} in rows
