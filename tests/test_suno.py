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
    vdir.mkdir(parents=True)
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


class FakeNotte:
    def __init__(self, clips_after):
        self.calls = []
        self.clips_after = clips_after
        self.clicked = False
        self.stopped = False

    def start(self):
        self.calls.append(("start",))

    def stop(self):
        self.stopped = True

    def page(self, *args):
        self.calls.append(args)
        if args[0] == "click":
            self.clicked = True
        return ""

    def eval_js(self, code):
        if "Lyrics editor" in code:
            return "true"
        if "a[href" in code:
            return suno.json.dumps(self.clips_after if self.clicked else ["/song/old"])
        return "true"


def test_generate_fills_form_and_returns_new_urls(tmp_path, monkeypatch):
    _write_variant(tmp_path, monkeypatch)
    fake = FakeNotte(["/song/old", "/song/n1", "/song/n2"])
    urls = suno.generate("song", "a", notte=fake)
    assert urls == ["https://suno.com/song/n1", "https://suno.com/song/n2"]
    fills = [c for c in fake.calls if c[0] == "fill"]
    assert [c[1] for c in fills] == [
        suno.LYRICS_SELECTOR,
        suno.STYLE_SELECTOR,
        suno.EXCLUDE_SELECTOR,
    ]
    assert fake.stopped


def test_generate_stops_session_on_failure(tmp_path, monkeypatch):
    _write_variant(tmp_path, monkeypatch)
    monkeypatch.setattr(suno, "CLIPS_TIMEOUT_SECONDS", 0)
    fake = FakeNotte(["/song/old"])
    with pytest.raises(suno.SunoError):
        suno.generate("song", "a", notte=fake)
    assert fake.stopped


def test_load_dotenv_fills_only_missing(tmp_path, monkeypatch):
    creds = tmp_path / "creds"
    creds.write_text("# c\nA_KEY=one\nB_KEY='two'\nSET_KEY=new\n", encoding="utf-8")
    monkeypatch.delenv("A_KEY", raising=False)
    monkeypatch.delenv("B_KEY", raising=False)
    monkeypatch.setenv("SET_KEY", "old")
    suno.load_dotenv(str(creds))
    assert suno.os.environ["A_KEY"] == "one"
    assert suno.os.environ["B_KEY"] == "two"
    assert suno.os.environ["SET_KEY"] == "old"


def test_generate_needs_credentials(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_variant(tmp_path, monkeypatch)
    monkeypatch.delenv("NOTTE_API_KEY", raising=False)
    monkeypatch.delenv("SUNO_PROFILE_ID", raising=False)
    with pytest.raises(suno.SunoError):
        suno.generate("song", "a")
