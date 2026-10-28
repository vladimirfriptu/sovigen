import re
from urllib.parse import parse_qs, urlparse

_ID = re.compile(r"[A-Za-z0-9_-]{11}")
_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"}
_PATH_PREFIXES = ("shorts", "embed", "live")


def video_id(url: str):
    parsed = urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        return None
    host = (parsed.hostname or "").lower()
    candidate = None
    if host == "youtu.be":
        candidate = parsed.path.lstrip("/")
    elif host in _HOSTS:
        parts = [part for part in parsed.path.split("/") if part]
        if parsed.path == "/watch":
            candidate = (parse_qs(parsed.query).get("v") or [""])[0]
        elif len(parts) == 2 and parts[0] in _PATH_PREFIXES:
            candidate = parts[1]
    if candidate and _ID.fullmatch(candidate):
        return candidate
    return None


def watch_url(vid: str) -> str:
    return f"https://www.youtube.com/watch?v={vid}"


def embed_url(vid: str) -> str:
    return f"https://www.youtube-nocookie.com/embed/{vid}"


def canonical(url: str) -> str:
    vid = video_id(url)
    if vid is None:
        raise ValueError("Это не ссылка на видео YouTube")
    return watch_url(vid)
