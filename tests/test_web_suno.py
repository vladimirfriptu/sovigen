import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from sovigen import meta as meta_mod
from sovigen import web

SUNO_MD = "## Style\n\n```\nfolk\n```\n\n## Exclude Styles\n\n```\ndrums\n```\n"
LYRICS_MD = "# T\n\n[Verse]\nline one\n"


class FakeBridge:
    def __init__(self, online=True, results=None):
        self.online = online
        self.results = list(results or [{"ok": True, "clips": 2, "error": ""}])
        self.submitted = []

    def extension_online(self, max_age):
        return self.online

    def wait_for_extension(self, timeout):
        return True

    def submit(self, job):
        self.submitted.append(job)
        return "1"

    def wait_result(self, job_id, timeout):
        return self.results.pop(0)


@pytest.fixture
def studio(tmp_path, monkeypatch):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    sdir = tmp_path / "song-13"
    vdir = sdir / "variants" / "a"
    vdir.mkdir(parents=True)
    (vdir / "suno.md").write_text(SUNO_MD, encoding="utf-8")
    (vdir / "lyrics.md").write_text(LYRICS_MD, encoding="utf-8")
    meta_mod.write_meta(sdir, meta_mod.new_meta("Song", "song-13", "2026-10-28"))

    server = ThreadingHTTPServer(("127.0.0.1", 0), web.SovigenHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_address[1]}", sdir, monkeypatch
    server.shutdown()
    server.server_close()


def _request(base, path, body=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, headers=headers or {}, method="POST" if data else "GET")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


JSON = {"Content-Type": "application/json"}
PAYLOAD = {"slug": "song-13", "variant": "a"}


def test_status_is_unavailable_without_a_bridge(studio):
    base, _, monkeypatch = studio
    monkeypatch.setattr(web, "_bridge", None)
    assert _request(base, "/api/suno/status") == (200, {"available": False})


def test_status_follows_the_extension(studio):
    base, _, monkeypatch = studio
    monkeypatch.setattr(web, "_bridge", FakeBridge(online=True))
    assert _request(base, "/api/suno/status")[1] == {"available": True}
    monkeypatch.setattr(web, "_bridge", FakeBridge(online=False))
    assert _request(base, "/api/suno/status")[1] == {"available": False}


def test_send_requires_json_content_type(studio):
    base, _, monkeypatch = studio
    monkeypatch.setattr(web, "_bridge", FakeBridge())
    status, _ = _request(base, "/api/suno/send", PAYLOAD, {"Content-Type": "text/plain"})
    assert status == 415


def test_send_rejects_a_foreign_origin(studio):
    base, _, monkeypatch = studio
    bridge = FakeBridge()
    monkeypatch.setattr(web, "_bridge", bridge)
    status, _ = _request(base, "/api/suno/send", PAYLOAD, {**JSON, "Origin": "https://evil.example"})
    assert status == 403
    assert bridge.submitted == []


def test_send_refuses_when_the_extension_is_offline(studio):
    base, _, monkeypatch = studio
    bridge = FakeBridge(online=False)
    monkeypatch.setattr(web, "_bridge", bridge)
    status, result = _request(base, "/api/suno/send", PAYLOAD, JSON)
    assert status == 409
    assert result["ok"] is False
    assert bridge.submitted == []


def test_send_submits_the_variant_and_counts_the_clips(studio):
    base, sdir, monkeypatch = studio
    bridge = FakeBridge()
    monkeypatch.setattr(web, "_bridge", bridge)
    status, result = _request(base, "/api/suno/send", PAYLOAD, JSON)
    assert status == 200
    assert result["ok"] is True and result["clips"] == 2
    assert bridge.submitted[0]["title"] == "13_a"
    assert meta_mod.read_meta(sdir)["suno_takes"] == 2


def test_send_unknown_variant_is_a_400(studio):
    base, _, monkeypatch = studio
    monkeypatch.setattr(web, "_bridge", FakeBridge())
    status, result = _request(base, "/api/suno/send", {"slug": "song-13", "variant": "z"}, JSON)
    assert status == 400
    assert "no variant" in result["error"]
