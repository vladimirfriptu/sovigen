import subprocess

import pytest

from sovigen import meta
from sovigen.cli import main


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
    assert "draft" in out


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
    assert main(["ready", "flow-song"]) == 0
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
