import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from sovigen import meta as meta_mod
from sovigen import web

VIDEO_ID = "dQw4w9WgXcQ"
SUNO_MD = "## Style\n\n```\nfolk\n```\n\n## Exclude Styles\n\n```\ndrums\n```\n"
LYRICS_MD = "# T\n\n[Verse]\nline one\n"
YOUTUBE_MD = "## Заголовок\n\nMy title\n\n## Описание\n\nMy description\n\n## Теги\n\npsalm, worship\n"


def _song(lib, slug, stage, **extra):
    sdir = lib / slug
    sdir.mkdir(parents=True)
    data = meta_mod.new_meta(slug.upper(), slug, "2026-10-28")
    data["stage"] = stage
    data.update(extra)
    meta_mod.write_meta(sdir, data)
    return sdir


@pytest.fixture
def studio(tmp_path, monkeypatch):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    monkeypatch.setattr(web, "_bridge", None)

    prompted = _song(
        tmp_path, "psalm-13", "prompted",
        variants=[{"id": "a", "style": "intimate-folk", "angle": "an angle"}],
    )
    vdir = prompted / "variants" / "a"
    vdir.mkdir(parents=True)
    (vdir / "suno.md").write_text(SUNO_MD, encoding="utf-8")
    (vdir / "lyrics.md").write_text(LYRICS_MD, encoding="utf-8")

    _song(tmp_path, "psalm-12", "recorded")
    video = _song(tmp_path, "psalm-11", "pre-published")
    (video / "youtube.mp4").write_bytes(b"x" * 2048)
    (video / "youtube.md").write_text(YOUTUBE_MD, encoding="utf-8")
    _song(tmp_path, "psalm-10", "published", youtube_url=f"https://www.youtube.com/watch?v={VIDEO_ID}")
    _song(tmp_path, "psalm-9", "published")
    _song(tmp_path, "psalm-8", "idea")

    server = ThreadingHTTPServer(("127.0.0.1", 0), web.SovigenHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}", tmp_path
    server.shutdown()
    server.server_close()


def _get(base, path):
    try:
        with urllib.request.urlopen(base + path) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("utf-8")


def _post(base, path, fields):
    boundary = "xBOUNDARYx"
    parts = []
    for key, value in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'
        )
    payload = ("".join(parts) + f"--{boundary}--\r\n").encode()
    req = urllib.request.Request(
        base + path,
        data=payload,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode("utf-8")


def test_home_selects_the_first_song_waiting_for_the_owner(studio):
    base, _ = studio
    status, page = _get(base, "/")
    assert status == 200
    assert "Загрузить трек" in page or "Загрузить обложку" in page or "Загрузить на YouTube" in page


def test_sidebar_groups_songs_by_turn(studio):
    base, _ = studio
    _, page = _get(base, "/")
    assert "Ваш ход" in page and "Ход Claude" in page and "Опубликовано" in page
    assert "/?song=psalm-13" in page


def test_prompted_song_shows_a_strip_per_variant_and_hidden_send_button(studio):
    base, _ = studio
    _, page = _get(base, "/?song=psalm-13")
    assert 'class="strip active"' in page
    assert "folk" in page and "line one" in page
    assert 'class="btn primary send-suno"' in page and "hidden" in page


def test_recorded_song_asks_for_a_cover(studio):
    base, _ = studio
    _, page = _get(base, "/?song=psalm-12")
    assert 'action="/record-cover"' in page


def test_pre_published_song_offers_download_copy_fields_and_publish_form(studio):
    base, _ = studio
    _, page = _get(base, "/?song=psalm-11")
    assert "/download/psalm-11" in page
    assert "My title" in page and "My description" in page
    assert 'action="/publish"' in page


def test_published_song_with_a_link_embeds_the_video(studio):
    base, _ = studio
    _, page = _get(base, "/?song=psalm-10")
    assert f"https://www.youtube-nocookie.com/embed/{VIDEO_ID}" in page
    assert "<iframe" in page


def test_published_song_without_a_link_has_no_player_and_asks_for_one(studio):
    base, _ = studio
    _, page = _get(base, "/?song=psalm-9")
    assert "<iframe" not in page
    assert "Ссылка на видео пока не сохранена" in page
    assert 'action="/youtube"' in page


def test_unknown_song_falls_back_to_the_default(studio):
    base, _ = studio
    status, page = _get(base, "/?song=nope")
    assert status == 200 and "psalm-" in page


def test_publish_stores_the_link_and_moves_the_stage(studio):
    base, lib = studio
    status, page = _post(base, "/publish", {"slug": "psalm-11", "url": f"https://youtu.be/{VIDEO_ID}"})
    assert status == 200
    assert "<iframe" in page
    data = meta_mod.read_meta(lib / "psalm-11")
    assert data["stage"] == "published"
    assert data["youtube_url"].endswith(VIDEO_ID)


def test_publish_without_a_link_still_publishes(studio):
    base, lib = studio
    status, _ = _post(base, "/publish", {"slug": "psalm-11", "url": ""})
    assert status == 200
    assert meta_mod.read_meta(lib / "psalm-11")["stage"] == "published"


def test_publish_rejects_a_foreign_link_and_keeps_the_stage(studio):
    base, lib = studio
    status, page = _post(base, "/publish", {"slug": "psalm-11", "url": "https://example.com/x"})
    assert status == 400
    assert "не ссылка на видео YouTube" in page
    assert meta_mod.read_meta(lib / "psalm-11")["stage"] == "pre-published"


def test_publish_refuses_a_song_that_is_not_waiting(studio):
    base, _ = studio
    status, _ = _post(base, "/publish", {"slug": "psalm-12", "url": ""})
    assert status == 400


def test_youtube_route_saves_a_link_for_a_published_song(studio):
    base, lib = studio
    status, page = _post(base, "/youtube", {"slug": "psalm-9", "url": f"https://youtu.be/{VIDEO_ID}"})
    assert status == 200 and "<iframe" in page
    assert meta_mod.read_meta(lib / "psalm-9")["youtube_url"].endswith(VIDEO_ID)


def test_titles_and_links_are_escaped(studio):
    base, lib = studio
    data = meta_mod.read_meta(lib / "psalm-8")
    data["title"] = '<script>alert(1)</script>'
    meta_mod.write_meta(lib / "psalm-8", data)
    _, page = _get(base, "/?song=psalm-8")
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_pre_published_song_without_a_video_file_still_offers_fields_and_publishing(studio):
    base, lib = studio
    (lib / "psalm-11" / "youtube.mp4").unlink()
    _, page = _get(base, "/?song=psalm-11")
    assert "/download/psalm-11" not in page
    assert "не хранятся в git" in page
    assert "My title" in page
    assert 'action="/publish"' in page
