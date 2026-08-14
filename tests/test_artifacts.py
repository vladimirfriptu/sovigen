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


def test_missing_for_stage_names_the_ambiguous_files(song):
    (song / "a.png").write_bytes(b"")
    (song / "b.jpg").write_bytes(b"")
    (song / "youtube.md").write_text("x", encoding="utf-8")
    reported = artifacts.missing_for_stage(song, "ready")
    assert len(reported) == 1
    assert "Multiple image files" in reported[0]
    assert "a.png" in reported[0] and "b.jpg" in reported[0]


def test_missing_for_stage_ambiguous_audio_is_not_reported_as_absent(song):
    (song / "take-1.mp3").write_bytes(b"")
    (song / "take-2.mp3").write_bytes(b"")
    reported = artifacts.missing_for_stage(song, "recorded")
    assert reported != [artifacts.AUDIO]
    assert "take-1.mp3" in reported[0]


def test_idea_stage_requires_nothing(song):
    assert artifacts.missing_for_stage(song, "idea") == []


def test_variant_ids_empty_without_variants_dir(song):
    assert artifacts.variant_ids(song) == []


def test_variant_ids_sorted(song):
    for name in ("c", "a", "b"):
        (song / "variants" / name).mkdir(parents=True)
    assert artifacts.variant_ids(song) == ["a", "b", "c"]


def test_variant_ids_ignores_files(song):
    (song / "variants").mkdir()
    (song / "variants" / "notes.txt").write_text("x", encoding="utf-8")
    assert artifacts.variant_ids(song) == []


def test_lyrics_requirement_satisfied_by_a_variant(song):
    (song / "variants" / "a").mkdir(parents=True)
    (song / "variants" / "a" / "lyrics.md").write_text("текст", encoding="utf-8")
    assert artifacts.missing_for_stage(song, "lyrics") == []


def test_suno_requirement_satisfied_by_a_variant(song):
    (song / "variants" / "b").mkdir(parents=True)
    (song / "variants" / "b" / "suno.md").write_text("Style", encoding="utf-8")
    assert artifacts.missing_for_stage(song, "prompted") == []


def test_lyrics_requirement_still_satisfied_by_the_root_file(song):
    (song / "lyrics.md").write_text("текст", encoding="utf-8")
    assert artifacts.missing_for_stage(song, "lyrics") == []


def test_lyrics_missing_reports_the_plain_name(song):
    (song / "variants" / "a").mkdir(parents=True)
    assert artifacts.missing_for_stage(song, "lyrics") == ["lyrics.md"]


def test_brief_requirement_is_not_fanned_out(song):
    (song / "variants" / "a").mkdir(parents=True)
    (song / "variants" / "a" / "brief.md").write_text("концепт", encoding="utf-8")
    assert artifacts.missing_for_stage(song, "brief") == ["brief.md"]
