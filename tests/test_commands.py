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
    _make_song(lib, "idea-one", stage="idea")
    _fake_ffmpeg_ok(monkeypatch)
    built = commands.cmd_build_all()
    assert built == ["ready-one"]
    assert meta.read_meta(lib / "ready-one")["stage"] == "pre-published"
    assert meta.read_meta(lib / "idea-one")["stage"] == "idea"


def test_build_all_skips_dirs_without_meta(lib, monkeypatch):
    (lib / "junk").mkdir(parents=True)
    _fake_ffmpeg_ok(monkeypatch)
    assert commands.cmd_build_all() == []


def test_advance_moves_to_next_stage(lib):
    sdir = _make_song(lib, "s", stage="idea", with_inputs=False)
    (sdir / "brief.md").write_text("x", encoding="utf-8")
    assert commands.cmd_advance("s") == ("idea", "brief")
    assert meta.read_meta(sdir)["stage"] == "brief"


def test_advance_refuses_without_required_file(lib):
    _make_song(lib, "s", stage="idea", with_inputs=False)
    with pytest.raises(commands.CommandError) as err:
        commands.cmd_advance("s")
    assert "missing: brief.md" in str(err.value)


def test_advance_at_final_stage_is_idempotent(lib):
    _make_song(lib, "s", stage="published", with_inputs=False)
    assert commands.cmd_advance("s") == ("published", "published")


def test_advance_records_history(lib):
    sdir = _make_song(lib, "s", stage="idea", with_inputs=False)
    (sdir / "brief.md").write_text("x", encoding="utf-8")
    commands.cmd_advance("s")
    history = meta.read_meta(sdir)["stage_history"]
    assert history[-1]["stage"] == "brief"


def test_publish_sets_stage(lib):
    _make_song(lib, "song-d", stage="pre-published")
    commands.cmd_publish("song-d")
    assert meta.read_meta(lib / "song-d")["stage"] == "published"


def test_status_lists_rows(lib):
    _make_song(lib, "song-e", stage="ready")
    rows = commands.cmd_status()
    assert {"slug": "song-e", "stage": "ready", "title": "song-e", "turn": "claude"} in rows


def test_status_reports_turn(lib):
    _make_song(lib, "a", stage="prompted", with_inputs=False)
    _make_song(lib, "b", stage="lyrics", with_inputs=False)
    _make_song(lib, "c", stage="published", with_inputs=False)
    rows = {row["slug"]: row["turn"] for row in commands.cmd_status()}
    assert rows == {"a": "you", "b": "claude", "c": "-"}


def test_import_audio_to_canonical_name(lib, tmp_path):
    sdir = _make_song(lib, "s", stage="prompted", with_inputs=False)
    src = tmp_path / "Suno v5 take 3.mp3"
    src.write_bytes(b"audio")
    dest = commands.cmd_import("s", src)
    assert dest == sdir / "track.mp3"
    assert dest.read_bytes() == b"audio"


def test_import_keeps_source_file(lib, tmp_path):
    _make_song(lib, "s", stage="prompted", with_inputs=False)
    src = tmp_path / "take.mp3"
    src.write_bytes(b"audio")
    commands.cmd_import("s", src)
    assert src.exists()


def test_import_image_keeps_extension(lib, tmp_path):
    sdir = _make_song(lib, "s", stage="recorded", with_inputs=False)
    src = tmp_path / "Gemini_Generated_Image.png"
    src.write_bytes(b"img")
    assert commands.cmd_import("s", src) == sdir / "cover.png"


def test_import_moves_previous_file_to_raw(lib, tmp_path):
    sdir = _make_song(lib, "s", stage="prompted", with_inputs=False)
    (sdir / "track.mp3").write_bytes(b"old")
    src = tmp_path / "new.mp3"
    src.write_bytes(b"new")
    commands.cmd_import("s", src)
    assert (sdir / "track.mp3").read_bytes() == b"new"
    assert (sdir / "raw" / "track.mp3").read_bytes() == b"old"


def test_import_three_successive_audio_files_keep_all_payloads(lib, tmp_path):
    sdir = _make_song(lib, "s", stage="prompted", with_inputs=False)
    src1 = tmp_path / "v1.mp3"
    src1.write_bytes(b"v1")
    src2 = tmp_path / "v2.mp3"
    src2.write_bytes(b"v2")
    src3 = tmp_path / "v3.mp3"
    src3.write_bytes(b"v3")
    commands.cmd_import("s", src1)
    commands.cmd_import("s", src2)
    commands.cmd_import("s", src3)
    assert (sdir / "track.mp3").read_bytes() == b"v3"
    raw_dir = sdir / "raw"
    stashed = {p.name: p.read_bytes() for p in raw_dir.glob("track*.mp3")}
    assert stashed == {"track.mp3": b"v1", "track-2.mp3": b"v2"}


def test_import_rejects_unknown_extension(lib, tmp_path):
    _make_song(lib, "s", stage="prompted", with_inputs=False)
    src = tmp_path / "notes.txt"
    src.write_text("x", encoding="utf-8")
    with pytest.raises(commands.CommandError) as err:
        commands.cmd_import("s", src)
    assert "unsupported file type" in str(err.value)


def test_import_missing_source(lib, tmp_path):
    _make_song(lib, "s", stage="prompted", with_inputs=False)
    with pytest.raises(commands.CommandError):
        commands.cmd_import("s", tmp_path / "nope.mp3")


def test_import_rejects_source_inside_song_folder_and_keeps_it(lib):
    sdir = _make_song(lib, "s", stage="prompted", with_inputs=False)
    legacy = sdir / "Псалом 3.mp3"
    legacy.write_bytes(b"legacy take")
    with pytest.raises(commands.CommandError) as err:
        commands.cmd_import("s", legacy)
    assert "already inside" in str(err.value)
    assert legacy.read_bytes() == b"legacy take"
    assert list((sdir / "raw").iterdir()) == []


def test_import_rejects_source_inside_raw_and_keeps_it(lib):
    sdir = _make_song(lib, "s", stage="prompted", with_inputs=False)
    stashed = sdir / "raw" / "old.mp3"
    stashed.write_bytes(b"old take")
    with pytest.raises(commands.CommandError):
        commands.cmd_import("s", stashed)
    assert stashed.read_bytes() == b"old take"


def test_import_failed_copy_keeps_previous_take_in_place(lib, tmp_path, monkeypatch):
    sdir = _make_song(lib, "s", stage="prompted", with_inputs=False)
    (sdir / "track.mp3").write_bytes(b"old")
    src = tmp_path / "new.mp3"
    src.write_bytes(b"new")

    def full_disk(source, destination, **kwargs):
        raise OSError("No space left on device")

    monkeypatch.setattr(commands.shutil, "copy2", full_disk)
    with pytest.raises(commands.CommandError):
        commands.cmd_import("s", src)
    assert (sdir / "track.mp3").read_bytes() == b"old"
    assert list((sdir / "raw").iterdir()) == []
    assert [p.name for p in sdir.glob(".sovigen-import-*")] == []


def test_import_leaves_no_staging_file_behind(lib, tmp_path):
    sdir = _make_song(lib, "s", stage="prompted", with_inputs=False)
    src = tmp_path / "take.mp3"
    src.write_bytes(b"audio")
    commands.cmd_import("s", src)
    assert [p.name for p in sdir.glob(".sovigen-*")] == []
