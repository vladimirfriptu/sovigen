"""Small localhost upload-and-build interface for Sovigen."""

import json
from email import policy
from email.parser import BytesParser
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
import os
import re
import tempfile
from threading import Lock

from . import commands, meta, paths, suno, web_ui
from .suno_bridge import Bridge
from .artifacts import VIDEO_FILENAME
from .inputs import AUDIO_EXTS, IMAGE_EXTS, InputError, find_audio, find_image


MAX_UPLOAD_BYTES = 160 * 1024 * 1024
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
_BUILD_LOCK = Lock()
_SUNO_LOCK = Lock()
SUNO_ONLINE_SECONDS = 10
_bridge = None


def _suno_available() -> bool:
    return _bridge is not None and _bridge.extension_online(SUNO_ONLINE_SECONDS)


def _start_bridge() -> None:
    global _bridge
    try:
        bridge = Bridge(int(os.environ.get("SOVIGEN_SUNO_PORT", 8787)))
        bridge.start()
    except OSError:
        # Port taken, for example by a running `just suno`: the button stays hidden.
        return
    _bridge = bridge


def _ready_songs() -> list[dict]:
    songs = []
    for slug in paths.list_song_slugs():
        song_dir = paths.song_dir(slug)
        if not meta.has_meta(song_dir):
            continue
        try:
            data = meta.read_meta(song_dir)
        except (OSError, ValueError):
            continue
        if data.get("stage") == "ready":
            songs.append({"slug": slug, "title": data.get("title", slug)})
    return songs


def _songs_at_stage(stage: str) -> list[dict]:
    songs = []
    for slug in paths.list_song_slugs():
        song_dir = paths.song_dir(slug)
        if not meta.has_meta(song_dir):
            continue
        try:
            data = meta.read_meta(song_dir)
        except (OSError, ValueError):
            continue
        if data.get("stage") == stage:
            songs.append({"slug": slug, "dir": song_dir, **data})
    return songs


def _prompted_songs() -> list[dict]:
    songs = []
    for slug in paths.list_song_slugs():
        song_dir = paths.song_dir(slug)
        if not meta.has_meta(song_dir):
            continue
        try:
            data = meta.read_meta(song_dir)
        except (OSError, ValueError):
            continue
        if data.get("stage") == "prompted" and data.get("variants"):
            songs.append({"slug": slug, "dir": song_dir, **data})
    return songs


def _published_videos() -> list[dict]:
    return [
        song for song in _songs_at_stage("pre-published")
        if (song["dir"] / VIDEO_FILENAME).is_file()
    ]


def _without_frontmatter(document: str) -> str:
    if document.startswith("---\n"):
        _, _, body = document.split("---", 2)
        return body.strip()
    return document.strip()


def _section(document: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)",
        document,
        flags=re.MULTILINE | re.DOTALL,
    )
    return match.group(1).strip() if match else ""


def _code_value(section: str) -> str:
    match = re.search(r"```[^\n]*\n(.*?)\n```", section, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _youtube_fields(song_dir: Path) -> dict[str, str | bool]:
    path = song_dir / "youtube.md"
    document = _without_frontmatter(path.read_text(encoding="utf-8")) if path.is_file() else ""
    tags_section = _section(document, "Теги")
    tags = "\n".join(
        line.strip() for line in tags_section.splitlines()
        if line.strip() and not line.lstrip().startswith(">")
    ).strip()
    return {
        "title": _section(document, "Заголовок"),
        "description": _section(document, "Описание"),
        "tags": tags,
        "tags_draft": "чернов" in tags_section.lower() or "предлож" in tags_section.lower(),
    }


def _lyrics_value(path: Path) -> str:
    if not path.is_file():
        return ""
    document = _without_frontmatter(path.read_text(encoding="utf-8"))
    document = re.split(r"^## Соответствие источнику\s*$", document, maxsplit=1, flags=re.MULTILINE)[0]
    document = re.sub(r"^# .*\n+", "", document, count=1)
    return document.strip()


def _variant_cards(song: dict) -> list[dict]:
    chosen = song.get("chosen_variant")
    cards = []
    for variant in song.get("variants", []):
        variant_id = str(variant.get("id", ""))
        if not variant_id:
            continue
        variant_dir = song["dir"] / "variants" / variant_id
        suno_path = variant_dir / "suno.md"
        document = _without_frontmatter(
            suno_path.read_text(encoding="utf-8") if suno_path.is_file() else ""
        )
        mode = _section(document, "Режим генерации")
        advice = _section(document, "Советы по генерации")
        cards.append({
            "id": variant_id,
            "card": str(variant.get("style") or "стиль не указан"),
            "angle": str(variant.get("angle") or ""),
            "lyrics": _lyrics_value(variant_dir / "lyrics.md"),
            "style": _code_value(_section(document, "Style")),
            "exclude": _code_value(_section(document, "Exclude Styles")),
            "guidance": "\n\n".join(value for value in (mode, advice) if value),
            "chosen": variant_id == chosen,
        })
    return cards


def _song_detail(slug: str) -> dict:
    song_dir = paths.song_dir(slug)
    data = meta.read_meta(song_dir)
    detail = {
        "slug": slug,
        "title": str(data.get("title", slug)),
        "stage": data.get("stage", "?"),
        "takes": data.get("suno_takes", 0),
        "youtube_url": data.get("youtube_url"),
        "variants": [],
        "youtube": None,
    }
    if detail["stage"] == "prompted":
        detail["variants"] = _variant_cards({"dir": song_dir, **data})
    if detail["stage"] == "pre-published":
        detail["youtube"] = _youtube_fields(song_dir)
        video = song_dir / VIDEO_FILENAME
        detail["video_mb"] = video.stat().st_size / (1024 * 1024) if video.is_file() else None
    return detail


def _page(message: str = "", *, kind: str = "", slug: str | None = None) -> bytes:
    rows = [row for row in commands.cmd_status() if row["stage"] not in ("?", "unreadable")]
    known = {row["slug"] for row in rows}
    if slug not in known:
        yours = [row for row in rows if row["turn"] == "you"]
        slug = (yours or rows or [{"slug": None}])[0]["slug"]
    selected = _song_detail(slug) if slug else None
    return web_ui.render_page(
        {"songs": rows, "selected": selected, "message": message, "kind": kind}
    )


def _read_form(handler: BaseHTTPRequestHandler) -> tuple[dict[str, str], dict[str, tuple[str, bytes]]]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        raise ValueError("Некорректный размер загрузки") from None
    if length <= 0 or length > MAX_UPLOAD_BYTES:
        raise ValueError("Размер загрузки должен быть от 1 байта до 160 МБ")
    content_type = handler.headers.get("Content-Type", "")
    if not content_type.lower().startswith("multipart/form-data;"):
        raise ValueError("Ожидалась форма загрузки файлов")
    body = handler.rfile.read(length)
    if len(body) != length:
        raise ValueError("Загрузка оборвалась")
    message = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode("ascii") + body
    )
    fields: dict[str, str] = {}
    files: dict[str, tuple[str, bytes]] = {}
    for part in message.iter_parts():
        disposition = part.get("Content-Disposition", "")
        name = part.get_param("name", header="content-disposition")
        if not name:
            continue
        filename = part.get_filename()
        payload = part.get_payload(decode=True) or b""
        if filename:
            files[name] = (Path(filename).name, payload)
        else:
            charset = part.get_content_charset() or "utf-8"
            fields[name] = payload.decode(charset, errors="replace")
    return fields, files


def _save_upload(slug: str, field: tuple[str, bytes], canonical_name: str) -> Path:
    suffix = Path(field[0]).suffix.lower()
    with tempfile.TemporaryDirectory(prefix="sovigen-upload-") as temp_dir:
        source = Path(temp_dir) / f"{canonical_name}{suffix}"
        source.write_bytes(field[1])
        return commands.cmd_import(slug, source)


class SovigenHandler(BaseHTTPRequestHandler):
    server_version = "SovigenLocal/1.0"

    def log_message(self, fmt: str, *args) -> None:
        # Keep uploads and filenames out of routine server logs.
        return

    def _send_html(self, body: bytes, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _suno_send(self) -> None:
        origin = self.headers.get("Origin")
        if origin and urlparse(origin).netloc != self.headers.get("Host"):
            self._send_json({"ok": False, "error": "foreign origin"}, 403)
            return
        if self.headers.get("Content-Type", "").split(";")[0].strip() != "application/json":
            self._send_json({"ok": False, "error": "JSON expected"}, 415)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            slug = str(payload["slug"])
            variant = str(payload["variant"])
        except (ValueError, KeyError, TypeError):
            self._send_json({"ok": False, "error": "slug and variant are required"}, 400)
            return
        if not _suno_available():
            self._send_json({"ok": False, "error": "расширение Suno не на связи"}, 409)
            return
        if not _SUNO_LOCK.acquire(blocking=False):
            self._send_json({"ok": False, "error": "другая отправка ещё идёт"}, 409)
            return
        try:
            rows = suno.send_to_suno(slug, [variant], 0, _bridge)
        except suno.SunoError as err:
            self._send_json({"ok": False, "error": str(err)}, 400)
            return
        finally:
            _SUNO_LOCK.release()
        self._send_json(rows[0])

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/suno/status":
            self._send_json({"available": _suno_available()})
            return
        if parsed.path == "/":
            wanted = parse_qs(parsed.query).get("song", [None])[0]
            self._send_html(_page(slug=wanted))
            return
        if parsed.path.startswith("/download/"):
            slug = unquote(parsed.path.removeprefix("/download/"))
            # A successful build advances ready -> pre-published.
            if slug not in paths.list_song_slugs():
                self._send_html(_page("Песня не найдена.", kind="bad"), 404)
                return
            output = paths.song_dir(slug) / VIDEO_FILENAME
            if not output.is_file():
                self._send_html(_page("Видео ещё не собрано.", kind="bad", slug=slug), 404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(output.stat().st_size))
            self.send_header("Content-Disposition", 'attachment; filename="youtube.mp4"')
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            with output.open("rb") as stream:
                while chunk := stream.read(1024 * 1024):
                    self.wfile.write(chunk)
            return
        self._send_html(_page("Страница не найдена.", kind="bad"), 404)

    def do_POST(self) -> None:
        route = urlparse(self.path).path
        if route == "/api/suno/send":
            self._suno_send()
            return
        if route not in {"/record-track", "/record-cover", "/build", "/publish", "/youtube"}:
            self._send_html(_page("Страница не найдена.", kind="bad"), 404)
            return
        slug = ""
        try:
            fields, files = _read_form(self)
            with _BUILD_LOCK:
                slug = fields.get("slug", "")
                if route == "/record-track":
                    song = next((s for s in _songs_at_stage("prompted") if s["slug"] == slug), None)
                    if not song:
                        raise ValueError("Песня уже прошла этап загрузки трека или не найдена")
                    variant_id = fields.get("variant", "")
                    variants = {str(v.get("id")) for v in song.get("variants", [])}
                    if variant_id not in variants:
                        raise ValueError("Выбери вариант, по которому записан этот трек")
                    audio = files.get("audio")
                    if not audio or Path(audio[0]).suffix.lower() not in AUDIO_EXTS:
                        raise ValueError("Загрузите MP3, M4A или WAV")
                    commands.cmd_choose(slug, variant_id)
                    _save_upload(slug, audio, "track")
                    commands.cmd_advance(slug)
                    message = f"Трек загружен для варианта {variant_id.upper()}. Следующий шаг: обложка."
                    self._send_html(_page(message, kind="ok", slug=slug))
                    return

                if route == "/record-cover":
                    song = next((s for s in _songs_at_stage("recorded") if s["slug"] == slug), None)
                    if not song:
                        raise ValueError("Песня не ожидает обложку или не найдена")
                    cover = files.get("cover")
                    if not cover or Path(cover[0]).suffix.lower() not in IMAGE_EXTS:
                        raise ValueError("Загрузите JPG, PNG или WebP")
                    _save_upload(slug, cover, "cover")
                    commands.cmd_advance(slug)
                    message = "Обложка загружена. Проверь YouTube-заголовок и описание, затем собери видео."
                    self._send_html(_page(message, kind="ok", slug=slug))
                    return

                if route == "/publish":
                    if slug not in {song["slug"] for song in _songs_at_stage("pre-published")}:
                        raise ValueError("Песня не ожидает публикации или не найдена")
                    commands.cmd_publish(slug, fields.get("url", "").strip() or None)
                    self._send_html(_page("Песня отмечена опубликованной.", kind="ok", slug=slug))
                    return

                if route == "/youtube":
                    if slug not in paths.list_song_slugs():
                        raise ValueError("Песня не найдена")
                    commands.cmd_set_youtube(slug, fields.get("url", ""))
                    self._send_html(_page("Ссылка сохранена.", kind="ok", slug=slug))
                    return

                if slug not in {song["slug"] for song in _ready_songs()}:
                    raise ValueError("Выберите песню на стадии ready")
                audio = files.get("audio")
                cover = files.get("cover")
                if audio and Path(audio[0]).suffix.lower() not in AUDIO_EXTS:
                    raise ValueError("Загрузите MP3, M4A или WAV")
                if cover and Path(cover[0]).suffix.lower() not in IMAGE_EXTS:
                    raise ValueError("Загрузите JPG, PNG или WebP")
                song_dir = paths.song_dir(slug)
                output = song_dir / VIDEO_FILENAME
                if output.exists():
                    raise ValueError("В папке песни уже есть youtube.mp4. Переместите его перед новой сборкой.")
                if audio:
                    _save_upload(slug, audio, "track")
                if cover:
                    _save_upload(slug, cover, "cover")
                try:
                    find_audio(song_dir)
                    find_image(song_dir)
                except InputError as err:
                    raise ValueError(str(err)) from err
                commands.cmd_build(slug, static=True)
            self._send_html(_page("Видео собрано. Скачай его и загрузи на YouTube.", kind="ok", slug=slug))
        except (ValueError, commands.CommandError) as err:
            self._send_html(_page(str(err), kind="bad", slug=slug), 400)
        except Exception as err:
            self._send_html(_page(f"Не удалось выполнить действие: {err}", kind="bad", slug=slug), 500)


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    _start_bridge()
    server = ThreadingHTTPServer((host, port), SovigenHandler)
    print(f"Sovigen local builder: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSovigen local builder stopped")
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="sovigen-web")
    parser.add_argument("--host", default=os.environ.get("SOVIGEN_WEB_HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.environ.get("SOVIGEN_WEB_PORT", DEFAULT_PORT)))
    args = parser.parse_args(argv)
    serve(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
