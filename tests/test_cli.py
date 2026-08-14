import json
import subprocess

import pytest

from sovigen import commands, meta
from sovigen.cli import main
from sovigen import cli


@pytest.fixture
def lib(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path / "library"))
    return tmp_path / "library"


def test_new_then_status(lib, capsys):
    assert main(["new", "Hello World"]) == 0
    assert (lib / "hello-world" / "meta.json").exists()
    assert main(["status"]) == 0
    out = capsys.readouterr().out
    assert "hello-world" in out
    assert "idea" in out


def test_unknown_slug_returns_1(lib, capsys):
    rc = main(["build", "ghost"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "Song not found" in err


def test_full_flow(lib, monkeypatch, capsys):
    main(["new", "Flow Song"])
    sdir = lib / "flow-song"
    (sdir / "cover.png").write_bytes(b"")
    (sdir / "track.mp3").write_bytes(b"")
    meta.set_stage(sdir, "ready", "2026-06-22")
    assert meta.read_meta(sdir)["stage"] == "ready"

    def fake_run(cmd, capture_output=True, text=True):
        open(cmd[-1], "wb").close()

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert main(["build-all"]) == 0
    assert (sdir / "youtube.mp4").exists()
    assert meta.read_meta(sdir)["stage"] == "pre-published"
    assert main(["publish", "flow-song"]) == 0
    assert meta.read_meta(sdir)["stage"] == "published"


def test_status_json_is_parseable(lib, capsys):
    commands.cmd_new("Мій щит")
    assert cli.main(["status", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["slug"] == "мій-щит"
    assert payload[0]["stage"] == "idea"


def test_advance_reports_transition(lib, capsys):
    sdir = commands.cmd_new("Мій щит")
    (sdir / "brief.md").write_text("x", encoding="utf-8")
    assert cli.main(["advance", "мій-щит"]) == 0
    assert "idea -> brief" in capsys.readouterr().out


def test_import_of_a_file_already_in_the_song_folder_exits_nonzero(lib, capsys):
    main(["new", "Legacy"])
    sdir = lib / "legacy"
    legacy = sdir / "Псалом 3.mp3"
    legacy.write_bytes(b"legacy take")
    assert main(["import", "legacy", str(legacy)]) == 1
    assert legacy.read_bytes() == b"legacy take"
    assert "already inside" in capsys.readouterr().err


def test_reimport_then_advance_does_not_lose_the_previous_take(lib, tmp_path):
    main(["new", "Retake"])
    sdir = lib / "retake"
    meta.set_stage(sdir, "prompted", "2026-06-22")
    first = tmp_path / "v1.mp3"
    first.write_bytes(b"v1")
    second = tmp_path / "v2.mp3"
    second.write_bytes(b"v2")
    assert main(["import", "retake", str(first)]) == 0
    assert main(["import", "retake", str(second)]) == 0
    assert (sdir / "track.mp3").read_bytes() == b"v2"
    assert (sdir / "raw" / "track.mp3").read_bytes() == b"v1"
    assert main(["advance", "retake"]) == 0
    assert meta.read_meta(sdir)["stage"] == "recorded"


def test_advance_missing_file_exits_nonzero(lib, capsys):
    sdir = commands.cmd_new("Мій щит")
    (sdir / "brief.md").unlink()
    assert cli.main(["advance", "мій-щит"]) == 1
    assert "missing: brief.md" in capsys.readouterr().err
    assert not (sdir / "brief.md").exists()


def test_import_then_advance_walks_the_whole_pipeline(lib, tmp_path, monkeypatch,
                                                      capsys):
    def fake_run(cmd, capture_output=True, text=True):
        open(cmd[-1], "wb").close()

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert main(["new", "Flow Song"]) == 0
    sdir = lib / "flow-song"
    # Strip the templates the human is supposed to replace, so each gate below
    # is answered by real content rather than by the scaffolding.
    written_by_hand = {
        "brief": ("brief.md", "псалом 3, ночь и щит"),
        "lyrics": ("lyrics.md", "[Verse 1]\nТы мой щит"),
        "prompted": ("suno.md", "Style: worship ballad"),
    }
    for name, _ in written_by_hand.values():
        (sdir / name).unlink()
    (sdir / "youtube.md").unlink()

    for expected, (name, text) in written_by_hand.items():
        assert main(["advance", "flow-song"]) == 1
        assert f"missing: {name}" in capsys.readouterr().err
        (sdir / name).write_text(text, encoding="utf-8")
        assert main(["advance", "flow-song"]) == 0
        assert meta.read_meta(sdir)["stage"] == expected

    take = tmp_path / "Suno v5 take 2.mp3"
    take.write_bytes(b"audio")
    assert main(["import", "flow-song", str(take)]) == 0
    assert main(["advance", "flow-song"]) == 0
    assert meta.read_meta(sdir)["stage"] == "recorded"

    cover = tmp_path / "Gemini_Generated_Image.png"
    cover.write_bytes(b"img")
    assert main(["import", "flow-song", str(cover)]) == 0
    assert main(["advance", "flow-song"]) == 1
    assert "missing: youtube.md" in capsys.readouterr().err
    (sdir / "youtube.md").write_text("описание для ютуба", encoding="utf-8")
    assert main(["advance", "flow-song"]) == 0
    assert meta.read_meta(sdir)["stage"] == "ready"

    assert main(["build", "flow-song"]) == 0
    assert (sdir / "youtube.mp4").exists()
    assert meta.read_meta(sdir)["stage"] == "pre-published"
    assert main(["publish", "flow-song"]) == 0
    assert meta.read_meta(sdir)["stage"] == "published"


def test_status_json_reports_broken_song_without_dying(lib, capsys):
    commands.cmd_new("Good One")
    broken = commands.cmd_new("Bad One")
    (broken / "meta.json").write_text("", encoding="utf-8")
    assert cli.main(["status", "--json"]) == 0
    payload = {row["slug"]: row for row in json.loads(capsys.readouterr().out)}
    assert payload["good-one"]["stage"] == "idea"
    assert payload["bad-one"]["stage"] == "unreadable"


def test_choose_promotes_the_variant(lib, capsys):
    sdir = lib / "psalm-10"
    (sdir / "raw").mkdir(parents=True)
    meta.write_meta(sdir, meta.new_meta("Псалом 10", "psalm-10", "2026-08-14"))
    vdir = sdir / "variants" / "b"
    vdir.mkdir(parents=True)
    (vdir / "lyrics.md").write_text("варіант Б", encoding="utf-8")
    (vdir / "suno.md").write_text("Style Б", encoding="utf-8")
    assert main(["choose", "psalm-10", "b"]) == 0
    assert (sdir / "lyrics.md").read_text(encoding="utf-8") == "варіант Б"
    assert "chose b for psalm-10" in capsys.readouterr().out


def test_choose_reports_an_unknown_variant(lib, capsys):
    sdir = lib / "psalm-10"
    (sdir / "raw").mkdir(parents=True)
    meta.write_meta(sdir, meta.new_meta("Псалом 10", "psalm-10", "2026-08-14"))
    assert main(["choose", "psalm-10", "d"]) == 1
    assert "unknown variant: d" in capsys.readouterr().err
