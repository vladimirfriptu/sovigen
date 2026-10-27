"""Small localhost upload-and-build interface for Sovigen."""

from email import policy
from email.parser import BytesParser
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse
import os
import tempfile
from threading import Lock

from . import commands, meta, paths
from .artifacts import VIDEO_FILENAME
from .inputs import AUDIO_EXTS, IMAGE_EXTS


MAX_UPLOAD_BYTES = 160 * 1024 * 1024
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
_BUILD_LOCK = Lock()


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


def _page(message: str = "", *, download_slug: str | None = None) -> bytes:
    songs = _ready_songs()
    if songs:
        options = "".join(
            f'<option value="{escape(song["slug"], quote=True)}">'
            f'{escape(song["title"])} · {escape(song["slug"])}</option>'
            for song in songs
        )
        form = f"""
        <form action="/build" method="post" enctype="multipart/form-data">
          <label>Песня<select name="slug" required>{options}</select></label>
          <div class="uploads">
            <label class="drop">Аудио-файл <span>MP3, M4A или WAV</span>
              <input name="audio" type="file" accept=".mp3,.m4a,.wav,audio/*" required>
            </label>
            <label class="drop">Обложка <span>JPG, PNG или WebP</span>
              <input name="cover" type="file" accept=".jpg,.jpeg,.png,.webp,image/*" required>
            </label>
          </div>
          <label class="check"><input name="viz" type="checkbox" value="1"> Добавить спектр и прогресс-бар</label>
          <button type="submit">Собрать видео</button>
          <p class="hint">После загрузки файлы попадут в папку песни, а видео будет доступно для скачивания.</p>
        </form>"""
    else:
        form = '<div class="empty">Сейчас нет песен на стадии <code>ready</code>. Сначала продвиньте нужную песню до этой стадии командой <code>just advance &lt;slug&gt;</code>.</div>'

    notice = f'<div class="notice">{escape(message)}</div>' if message else ""
    download = ""
    if download_slug:
        download = (
            '<div class="success">Видео собрано. '
            f'<a class="download" href="/download/{escape(download_slug, quote=True)}">'
            'Скачать youtube.mp4</a></div>'
        )
    document = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sovigen · Сборка видео</title><style>
:root{{color-scheme:dark;--bg:#101114;--panel:#191b20;--muted:#a5a7ae;--gold:#e8b96a;--line:#30323a}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at 50% -20%,#34302a 0,#101114 48%);color:#f4f1eb;font:16px/1.5 system-ui,sans-serif;min-height:100vh;display:grid;place-items:center;padding:24px}}
main{{width:min(720px,100%);background:var(--panel);border:1px solid var(--line);border-radius:24px;padding:clamp(24px,5vw,48px);box-shadow:0 24px 90px #0008}}
.eyebrow{{color:var(--gold);letter-spacing:.16em;text-transform:uppercase;font-size:12px;font-weight:700}}h1{{font-size:clamp(30px,6vw,46px);line-height:1.08;margin:12px 0}}.intro,.hint{{color:var(--muted)}}form{{margin-top:32px}}label{{display:block;font-weight:650;margin:18px 0 8px}}select{{display:block;width:100%;margin-top:8px;background:#101114;color:inherit;border:1px solid var(--line);border-radius:12px;padding:14px;font:inherit}}
.uploads{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:18px 0}}.drop{{min-height:140px;border:1px dashed #68636a;border-radius:16px;padding:18px;display:flex;flex-direction:column;justify-content:space-between;background:#141519}}.drop span{{display:block;color:var(--muted);font-size:13px;font-weight:400}}input[type=file]{{font-size:13px;max-width:100%;margin-top:14px}}.check{{display:flex;gap:10px;align-items:center;font-weight:500}}button,.download{{display:inline-block;border:0;border-radius:12px;background:var(--gold);color:#181511;padding:14px 20px;font:700 16px system-ui;text-decoration:none;cursor:pointer;margin-top:12px}}button:hover,.download:hover{{background:#f2ca83}}.hint{{font-size:13px}}.empty,.notice,.success{{padding:16px;border-radius:14px;margin-top:24px;background:#24262c}}.success{{border:1px solid #526a54;background:#1b2920}}.download{{margin:12px 0 0}}code{{color:var(--gold)}}@media(max-width:560px){{.uploads{{grid-template-columns:1fr}}.drop{{min-height:120px}}}}
</style></head><body><main><div class="eyebrow">Sovigen · локально</div><h1>Собрать видео</h1><p class="intro">Загрузите готовый трек и обложку. Sovigen соберёт YouTube-видео из файлов и подготовит его к скачиванию.</p>{notice}{download}{form}</main>
<script>document.querySelector('form')?.addEventListener('submit',()=>{{const b=document.querySelector('button');b.disabled=true;b.textContent='Загружаю и собираю…'}})</script></body></html>"""
    return document.encode("utf-8")


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

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_html(_page())
            return
        if parsed.path.startswith("/download/"):
            slug = unquote(parsed.path.removeprefix("/download/"))
            # A successful build advances ready -> pre-published.
            if slug not in paths.list_song_slugs():
                self._send_html(_page("Песня не найдена."), 404)
                return
            output = paths.song_dir(slug) / VIDEO_FILENAME
            if not output.is_file():
                self._send_html(_page("Видео ещё не собрано."), 404)
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
        self._send_html(_page("Страница не найдена."), 404)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/build":
            self._send_html(_page("Страница не найдена."), 404)
            return
        try:
            fields, files = _read_form(self)
            with _BUILD_LOCK:
                slug = fields.get("slug", "")
                if slug not in {song["slug"] for song in _ready_songs()}:
                    raise ValueError("Выберите песню на стадии ready")
                audio = files.get("audio")
                cover = files.get("cover")
                if not audio or Path(audio[0]).suffix.lower() not in AUDIO_EXTS:
                    raise ValueError("Загрузите MP3, M4A или WAV")
                if not cover or Path(cover[0]).suffix.lower() not in IMAGE_EXTS:
                    raise ValueError("Загрузите JPG, PNG или WebP")
                song_dir = paths.song_dir(slug)
                output = song_dir / VIDEO_FILENAME
                if output.exists():
                    raise ValueError("В папке песни уже есть youtube.mp4. Переместите его перед новой сборкой.")
                with tempfile.TemporaryDirectory(prefix="sovigen-upload-") as temp_dir:
                    temp = Path(temp_dir)
                    audio_path = temp / ("track" + Path(audio[0]).suffix.lower())
                    cover_path = temp / ("cover" + Path(cover[0]).suffix.lower())
                    audio_path.write_bytes(audio[1])
                    cover_path.write_bytes(cover[1])
                    commands.cmd_import(slug, audio_path)
                    commands.cmd_import(slug, cover_path)
                commands.cmd_build(slug, viz=fields.get("viz") == "1")
            self._send_html(_page(download_slug=slug))
        except (ValueError, commands.CommandError) as err:
            self._send_html(_page(str(err)), 400)
        except Exception as err:
            self._send_html(_page(f"Не удалось собрать видео: {err}"), 500)


def serve(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
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
