import pytest

from sovigen import artifacts


@pytest.fixture
def song(tmp_path):
    sdir = tmp_path / "song"
    sdir.mkdir()
    return sdir


def _data():
    return {
        "title": "Мій щит",
        "slug": "mij-shchyt",
        "created": "2026-07-30",
        "source": "psalm-3",
        "series": "psalms",
        "language": "uk",
        "style": None,
    }


def test_render_creates_every_artifact(song):
    created = artifacts.render(song, _data())
    names = sorted(p.name for p in created)
    assert names == [
        "brief.md",
        "cover-prompt.md",
        "lyrics.md",
        "notes.md",
        "suno.md",
        "youtube.md",
    ]


def test_render_fills_frontmatter(song):
    artifacts.render(song, _data())
    text = (song / "brief.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "song: mij-shchyt" in text
    assert "source: psalm-3" in text
    assert "Мій щит" in text


def test_render_does_not_overwrite_existing(song):
    (song / "lyrics.md").write_text("мой текст", encoding="utf-8")
    artifacts.render(song, _data())
    assert (song / "lyrics.md").read_text(encoding="utf-8") == "мой текст"


def test_missing_for_stage_lists_absent_files(song):
    assert artifacts.missing_for_stage(song, "brief") == ["brief.md"]


def test_missing_for_stage_empty_when_present(song):
    (song / "brief.md").write_text("x", encoding="utf-8")
    assert artifacts.missing_for_stage(song, "brief") == []


def test_missing_for_stage_audio_marker(song):
    assert artifacts.missing_for_stage(song, "recorded") == ["audio (.mp3)"]
    (song / "track.mp3").write_bytes(b"")
    assert artifacts.missing_for_stage(song, "recorded") == []


def test_missing_for_stage_image_and_youtube(song):
    assert artifacts.missing_for_stage(song, "ready") == ["image", "youtube.md"]


def test_missing_for_stage_ignores_raw_folder(song):
    raw = song / "raw"
    raw.mkdir()
    (raw / "track.mp3").write_bytes(b"")
    assert artifacts.missing_for_stage(song, "recorded") == ["audio (.mp3)"]


def test_idea_stage_requires_nothing(song):
    assert artifacts.missing_for_stage(song, "idea") == []
