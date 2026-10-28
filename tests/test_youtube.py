import pytest

from sovigen import youtube

VIDEO_ID = "dQw4w9WgXcQ"


@pytest.mark.parametrize(
    "url",
    [
        f"https://www.youtube.com/watch?v={VIDEO_ID}",
        f"https://youtube.com/watch?v={VIDEO_ID}&t=42s",
        f"https://m.youtube.com/watch?v={VIDEO_ID}",
        f"https://music.youtube.com/watch?v={VIDEO_ID}",
        f"https://youtu.be/{VIDEO_ID}",
        f"https://youtu.be/{VIDEO_ID}?si=abc",
        f"https://www.youtube.com/shorts/{VIDEO_ID}",
        f"https://www.youtube.com/embed/{VIDEO_ID}",
        f"https://www.youtube.com/live/{VIDEO_ID}",
        f"  https://youtu.be/{VIDEO_ID}  ",
    ],
)
def test_video_id_accepts_youtube_forms(url):
    assert youtube.video_id(url) == VIDEO_ID


@pytest.mark.parametrize(
    "url",
    [
        "",
        "not a url",
        "https://example.com/watch?v=dQw4w9WgXcQ",
        "https://youtube.com.evil.example/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=short",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ%22%3E%3Cscript",
        "https://www.youtube.com/playlist?list=PL123",
        "javascript:alert(1)",
        "http://youtu.be/",
    ],
)
def test_video_id_rejects_everything_else(url):
    assert youtube.video_id(url) is None


def test_watch_url_is_canonical():
    assert youtube.watch_url(VIDEO_ID) == f"https://www.youtube.com/watch?v={VIDEO_ID}"


def test_embed_url_uses_the_privacy_domain():
    assert youtube.embed_url(VIDEO_ID) == f"https://www.youtube-nocookie.com/embed/{VIDEO_ID}"


def test_canonical_returns_watch_url_or_raises():
    assert youtube.canonical(f"https://youtu.be/{VIDEO_ID}?si=x") == youtube.watch_url(VIDEO_ID)
    with pytest.raises(ValueError):
        youtube.canonical("https://example.com/x")
