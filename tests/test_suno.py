import pytest

from sovigen import suno

SUNO_MD = """---
variant: a
---

# Title

## Style

```
folk, 70 bpm
```

## Exclude Styles

```
melisma, ad-libs
```
"""

LYRICS_MD = """---
variant: a
---

# Title — a

[Verse 1]
line one
line two

## Соответствие источнику

| a | b |
"""


def _write_variant(tmp_path, monkeypatch, suno_md=SUNO_MD, lyrics_md=LYRICS_MD):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    vdir = tmp_path / "song" / "variants" / "a"
    vdir.mkdir(parents=True, exist_ok=True)
    (vdir / "suno.md").write_text(suno_md, encoding="utf-8")
    (vdir / "lyrics.md").write_text(lyrics_md, encoding="utf-8")


def test_read_variant_extracts_fields(tmp_path, monkeypatch):
    _write_variant(tmp_path, monkeypatch)
    data = suno.read_variant("song", "a")
    assert data["style"] == "folk, 70 bpm"
    assert data["exclude"] == "melisma, ad-libs"
    assert data["lyrics"] == "[Verse 1]\nline one\nline two"


def test_read_variant_missing_section(tmp_path, monkeypatch):
    _write_variant(tmp_path, monkeypatch, suno_md="# x\n")
    with pytest.raises(suno.SunoError):
        suno.read_variant("song", "a")


def test_read_variant_missing_file(tmp_path, monkeypatch):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    with pytest.raises(suno.SunoError):
        suno.read_variant("song", "a")


def test_read_variant_style_too_long(tmp_path, monkeypatch):
    long_md = SUNO_MD.replace("folk, 70 bpm", "x" * 1001)
    _write_variant(tmp_path, monkeypatch, suno_md=long_md)
    with pytest.raises(suno.SunoError):
        suno.read_variant("song", "a")


def _add_meta(tmp_path):
    from sovigen import meta as meta_mod

    sdir = tmp_path / "song"
    sdir.mkdir(exist_ok=True)
    meta_mod.write_meta(sdir, meta_mod.new_meta("Song", "song", "2026-10-28"))
    return sdir


def _add_variant(tmp_path, name):
    vdir = tmp_path / "song" / "variants" / name
    vdir.mkdir(parents=True, exist_ok=True)
    (vdir / "suno.md").write_text(SUNO_MD, encoding="utf-8")
    (vdir / "lyrics.md").write_text(LYRICS_MD, encoding="utf-8")


class FakeBridge:
    def __init__(self, results, connected=True):
        self.results = list(results)
        self.connected = connected
        self.submitted = []

    def wait_for_extension(self, timeout):
        return self.connected

    def submit(self, job):
        self.submitted.append(job)
        return str(len(self.submitted))

    def wait_result(self, job_id, timeout):
        return self.results.pop(0)


OK = {"ok": True, "clips": 2, "error": ""}


def test_list_variants_sorted(tmp_path, monkeypatch):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    _add_variant(tmp_path, "b")
    _add_variant(tmp_path, "a")
    (tmp_path / "song" / "variants" / "c").mkdir()
    assert suno.list_variants("song") == ["a", "b"]


def test_list_variants_without_folder_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    (tmp_path / "song").mkdir()
    with pytest.raises(suno.SunoError):
        suno.list_variants("song")


def test_unknown_variant_raises_before_extension_is_awaited(tmp_path, monkeypatch):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    _add_variant(tmp_path, "a")
    bridge = FakeBridge([], connected=False)
    with pytest.raises(suno.SunoError, match="no variant 'z'"):
        suno.send_to_suno("song", ["z"], 0, bridge)


def test_no_extension_raises_with_hint(tmp_path, monkeypatch):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    _add_variant(tmp_path, "a")
    with pytest.raises(suno.SunoError, match="open suno.com/create"):
        suno.send_to_suno("song", ["a"], 0, FakeBridge([], connected=False))


def test_send_submits_in_order_and_sleeps_between(tmp_path, monkeypatch):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    _add_meta(tmp_path)
    _add_variant(tmp_path, "a")
    _add_variant(tmp_path, "b")
    bridge = FakeBridge([OK, OK])
    pauses = []
    results = suno.send_to_suno("song", ["a", "b"], 30, bridge, sleep=pauses.append)
    assert [r["variant"] for r in results] == ["a", "b"]
    assert [j["variant"] for j in bridge.submitted] == ["a", "b"]
    assert pauses == [30]
    assert bridge.submitted[0]["style"] == "folk, 70 bpm"


def test_send_stops_after_failed_variant(tmp_path, monkeypatch):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    _add_meta(tmp_path)
    _add_variant(tmp_path, "a")
    _add_variant(tmp_path, "b")
    bad = {"ok": False, "clips": 0, "error": "no new clips appeared"}
    bridge = FakeBridge([bad, OK])
    results = suno.send_to_suno("song", ["a", "b"], 0, bridge, sleep=lambda s: None)
    assert len(results) == 1
    assert results[0]["error"] == "no new clips appeared"
    assert len(bridge.submitted) == 1


def test_timeout_is_reported_as_failure(tmp_path, monkeypatch):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    _add_meta(tmp_path)
    _add_variant(tmp_path, "a")
    results = suno.send_to_suno("song", ["a"], 0, FakeBridge([None]))
    assert results[0]["ok"] is False


def test_successful_send_adds_clips_to_suno_takes(tmp_path, monkeypatch):
    from sovigen import meta as meta_mod

    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    sdir = _add_meta(tmp_path)
    _add_variant(tmp_path, "a")
    suno.send_to_suno("song", ["a"], 0, FakeBridge([OK]))
    assert meta_mod.read_meta(sdir)["suno_takes"] == 2

