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


def test_advance_missing_file_exits_nonzero(lib, capsys):
    sdir = commands.cmd_new("Мій щит")
    (sdir / "brief.md").unlink()
    assert cli.main(["advance", "мій-щит"]) == 1
    assert "missing: brief.md" in capsys.readouterr().err
