"""Small localhost upload-and-build interface for Sovigen."""

import json
from email import policy
from email.parser import BytesParser
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse
import os
import re
import tempfile
from threading import Lock

from . import commands, meta, paths, suno
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


def _render_suno_section() -> str:
    songs = _prompted_songs()
    if not songs:
        return '<div class="empty">Песен, ожидающих генерации в Suno, пока нет.</div>'

    html = []
    item_no = 0
    for song in songs:
        slug = song["slug"]
        song_dir = song["dir"]
        variants = song.get("variants", [])
        chosen = song.get("chosen_variant")
        variant_html = []
        for variant in variants:
            variant_id = str(variant.get("id", ""))
            if not variant_id:
                continue
            variant_dir = song_dir / "variants" / variant_id
            lyric_text = _lyrics_value(variant_dir / "lyrics.md")
            suno_path = variant_dir / "suno.md"
            suno_document = _without_frontmatter(
                suno_path.read_text(encoding="utf-8") if suno_path.is_file() else ""
            )
            style = _code_value(_section(suno_document, "Style"))
            exclude = _code_value(_section(suno_document, "Exclude Styles"))
            mode = _section(suno_document, "Режим генерации")
            advice = _section(suno_document, "Советы по генерации")
            guidance = "\n\n".join(value for value in (mode, advice) if value)
            item_no += 1
            suffix = str(item_no)
            selected = variant_id == chosen
            style_label = str(variant.get("style") or "стиль не указан")
            angle = str(variant.get("angle") or "")
            bundle = (
                f"LYRICS\n{lyric_text}\n\nSTYLE\n{style}\n\n"
                f"EXCLUDE STYLES\n{exclude}\n\nGENERATION NOTES\n{guidance}"
            )
            variant_html.append(f"""
            <details class="variant"{' open' if selected else ''}>
              <summary><span>Вариант {escape(variant_id.upper())} · {escape(style_label)}</span>
                <span class="chosen">{'Выбран' if selected else ''}</span></summary>
              <p class="angle">{escape(angle)}</p>
              <div class="send-row"><button class="send-suno" data-slug="{escape(slug, quote=True)}" data-variant="{escape(variant_id, quote=True)}" hidden>Отправить в Suno</button></div>
              <section class="copy-field">
                <div class="field-head"><h3>Lyrics · текст песни</h3><button class="copy" data-copy="lyrics-{suffix}">Копировать текст</button></div>
                <pre id="lyrics-{suffix}">{escape(lyric_text)}</pre>
              </section>
              <section class="copy-field">
                <div class="field-head"><h3>Style</h3><button class="copy" data-copy="style-{suffix}">Копировать</button></div>
                <pre id="style-{suffix}">{escape(style)}</pre>
              </section>
              <section class="copy-field">
                <div class="field-head"><h3>Exclude Styles</h3><button class="copy" data-copy="exclude-{suffix}">Копировать</button></div>
                <pre id="exclude-{suffix}">{escape(exclude)}</pre>
              </section>
              <section class="copy-field">
                <div class="field-head"><h3>Режим и советы</h3><button class="copy" data-copy="guidance-{suffix}">Копировать заметки</button></div>
                <pre id="guidance-{suffix}">{escape(guidance)}</pre>
              </section>
              <details class="all-fields"><summary>Показать комплект целиком</summary><pre id="all-{suffix}">{escape(bundle)}</pre></details>
              <button class="copy all-copy" data-copy="all-{suffix}">Копировать весь комплект</button>
            </details>""")
        if variant_html:
            html.append(f"""
            <details class="song" open>
              <summary><span>{escape(str(song.get('title', slug)))}</span><span class="song-stage">{escape(slug)} · ждёт Suno</span></summary>
              <div class="variants">{''.join(variant_html)}</div>
            </details>""")
    return "".join(html)


def _render_upload_section() -> str:
    cards = []
    for song in _songs_at_stage("prompted"):
        slug = str(song["slug"])
        title = escape(str(song.get("title", slug)))
        variants = song.get("variants", [])
        chosen = song.get("chosen_variant")
        options = []
        for variant in variants:
            variant_id = str(variant.get("id", ""))
            if not variant_id:
                continue
            style = str(variant.get("style") or "")
            selected = " selected" if variant_id == chosen else ""
            marker = " · выбран в проекте" if variant_id == chosen else ""
            options.append(
                f'<option value="{escape(variant_id, quote=True)}"{selected}>'
                f'{escape(variant_id.upper())} · {escape(style)}{marker}</option>'
            )
        placeholder = (
            "" if chosen else '<option value="" disabled selected>Выбери вариант записи</option>'
        )
        cards.append(f"""
        <article class="stage-card">
          <div class="stage-title"><h3>{title}</h3><span>ожидает аудио</span></div>
          <p>Укажи, по какому варианту записан этот файл. Выбор будет сохранён вместе с треком.</p>
          <form class="upload-step" action="/record-track" method="post" enctype="multipart/form-data">
            <input type="hidden" name="slug" value="{escape(slug, quote=True)}">
            <label>Вариант<select name="variant" required>{placeholder}{''.join(options)}</select></label>
            <label class="drop">Финальный трек <span>MP3, M4A или WAV · до 160 МБ</span>
              <input name="audio" type="file" accept=".mp3,.m4a,.wav,audio/*" required></label>
            <button type="submit">Загрузить трек</button>
          </form>
        </article>""")

    for song in _songs_at_stage("recorded"):
        slug = str(song["slug"])
        title = escape(str(song.get("title", slug)))
        cards.append(f"""
        <article class="stage-card">
          <div class="stage-title"><h3>{title}</h3><span>трек загружен</span></div>
          <p>Добавь обложку, чтобы перейти к сборке видео. Перед сборкой проверь, что YouTube-заголовок и описание подготовлены.</p>
          <form class="upload-step" action="/record-cover" method="post" enctype="multipart/form-data">
            <input type="hidden" name="slug" value="{escape(slug, quote=True)}">
            <label class="drop">Обложка <span>JPG, PNG или WebP · до 160 МБ</span>
              <input name="cover" type="file" accept=".jpg,.jpeg,.png,.webp,image/*" required></label>
            <button type="submit">Загрузить обложку и перейти к сборке</button>
          </form>
        </article>""")

    if not cards:
        return '<div class="empty">Сейчас нет песен, ожидающих загрузки трека или обложки.</div>'
    return "".join(cards)


def _render_youtube_section() -> str:
    songs = _published_videos()
    if not songs:
        return '<div class="empty">Готовых видео для YouTube пока нет.</div>'

    cards = []
    for index, song in enumerate(songs, 1):
        slug = str(song["slug"])
        title = str(song.get("title", slug))
        fields = _youtube_fields(song["dir"])
        output = song["dir"] / VIDEO_FILENAME
        size_mb = output.stat().st_size / (1024 * 1024)
        download_url = f"/download/{quote(slug, safe='')}"
        field_specs = (
            ("title", "1", "Заголовок"),
            ("description", "2", "Описание"),
            ("tags", "3", "Теги"),
        )
        copy_fields = []
        for name, step, label in field_specs:
            value = fields[name]
            if not value:
                continue
            copy_id = f"youtube-{name}-{index}"
            copy_fields.append(f"""
            <section class="copy-field youtube-field">
              <div class="field-head"><h3>Шаг {step} · {label}</h3>
                <button class="copy" data-copy="{copy_id}">Копировать {label.lower()}</button></div>
              <pre id="{copy_id}">{escape(value)}</pre>
            </section>""")
        tags_hint = (
            '<p class="hint draft-hint">Список тегов — черновое предложение; перед публикацией проверь его.</p>'
            if fields["tags_draft"] else ""
        )
        cards.append(f"""
        <article class="stage-card publish-card">
          <div class="stage-title"><h3>{escape(title)}</h3><span>готово к загрузке</span></div>
          <a class="download youtube-download" href="{download_url}">Скачать видео · {size_mb:.1f} МБ</a>
          <p class="section-intro youtube-intro">Скопируй поля по порядку и вставь в соответствующие поля YouTube.</p>
          {''.join(copy_fields)}{tags_hint}
        </article>""")
    return "".join(cards)


def _page(message: str = "", *, download_slug: str | None = None) -> bytes:
    songs = _ready_songs()
    suno_section = _render_suno_section()
    upload_section = _render_upload_section()
    youtube_section = _render_youtube_section()
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
            <label class="drop">Финальный трек <span>MP3, M4A или WAV — если ещё не загружен</span>
              <input name="audio" type="file" accept=".mp3,.m4a,.wav,audio/*">
            </label>
            <label class="drop">Обложка <span>JPG, PNG или WebP — если ещё не загружена</span>
              <input name="cover" type="file" accept=".jpg,.jpeg,.png,.webp,image/*">
            </label>
          </div>
          <button type="submit">Собрать видео</button>
          <p class="hint">Собирается видео со статичной обложкой. Уже загруженные файлы используются автоматически.</p>
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
<title>Sovigen · Студия</title><style>
:root{{color-scheme:dark;--bg:#101114;--panel:#191b20;--muted:#a5a7ae;--gold:#e8b96a;--line:#30323a}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at 50% -20%,#34302a 0,#101114 48%);color:#f4f1eb;font:16px/1.5 system-ui,sans-serif;min-height:100vh;display:flex;justify-content:center;align-items:flex-start;padding:24px}}
main{{width:min(1000px,100%);background:var(--panel);border:1px solid var(--line);border-radius:24px;padding:clamp(20px,4vw,44px);box-shadow:0 24px 90px #0008}}
.eyebrow{{color:var(--gold);letter-spacing:.16em;text-transform:uppercase;font-size:12px;font-weight:700}}h1{{font-size:clamp(30px,6vw,46px);line-height:1.08;margin:12px 0}}.intro,.hint{{color:var(--muted)}}form{{margin-top:32px}}label{{display:block;font-weight:650;margin:18px 0 8px}}select{{display:block;width:100%;margin-top:8px;background:#101114;color:inherit;border:1px solid var(--line);border-radius:12px;padding:14px;font:inherit}}
.uploads{{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:18px 0}}.drop{{min-height:140px;border:1px dashed #68636a;border-radius:16px;padding:18px;display:flex;flex-direction:column;justify-content:space-between;background:#141519}}.drop span{{display:block;color:var(--muted);font-size:13px;font-weight:400}}input[type=file]{{font-size:13px;max-width:100%;margin-top:14px}}.check{{display:flex;gap:10px;align-items:center;font-weight:500}}button,.download{{display:inline-block;border:0;border-radius:12px;background:var(--gold);color:#181511;padding:14px 20px;font:700 16px system-ui;text-decoration:none;cursor:pointer;margin-top:12px}}button:hover,.download:hover{{background:#f2ca83}}.hint{{font-size:13px}}.empty,.notice,.success{{padding:16px;border-radius:14px;margin-top:24px;background:#24262c}}.success{{border:1px solid #526a54;background:#1b2920}}.download{{margin:12px 0 0}}code{{color:var(--gold)}}@media(max-width:560px){{.uploads{{grid-template-columns:1fr}}.drop{{min-height:120px}}}}
.stage-card{{border:1px solid var(--line);border-radius:16px;background:#141519;padding:18px;margin:12px 0}}.stage-title{{display:flex;justify-content:space-between;gap:12px;align-items:center}}.stage-title h3{{font-size:17px}}.stage-title span{{color:var(--gold);font-size:12px;white-space:nowrap}}.stage-card>p{{color:var(--muted);font-size:14px}}.upload-step{{margin-top:12px}}.upload-step select{{max-width:100%}}.upload-step .drop{{min-height:110px}}.upload-step button{{width:100%}}.notice{{border:1px solid #6e5d35;background:#2b261c}}@media(max-width:560px){{.stage-card{{padding:14px}}.stage-title{{align-items:flex-start;flex-direction:column;gap:2px}}.upload-step button{{min-height:48px}}}}
.workspace{{margin-top:28px;padding-top:24px;border-top:1px solid var(--line);min-width:0}}.workspace h2{{font-size:21px;line-height:1.25;margin:0 0 8px}}.section-intro{{margin:0 0 16px;color:var(--muted);font-size:14px}}
.song,.variant,.all-fields{{border:1px solid var(--line);border-radius:14px;background:#141519;min-width:0}}.song{{margin:12px 0;overflow:hidden}}.song>summary,.variant>summary,.all-fields>summary{{cursor:pointer;list-style:none;padding:14px 16px;display:flex;justify-content:space-between;align-items:flex-start;gap:12px;font-weight:650}}summary::-webkit-details-marker{{display:none}}.song>summary:after,.variant>summary:after{{content:'＋';color:var(--gold);flex:0 0 auto}}details[open]>summary:after{{content:'−'}}.song-stage{{color:var(--muted);font-size:12px;font-weight:400;text-align:right;overflow-wrap:anywhere}}.variants{{padding:0 12px 12px}}.variant{{margin-top:10px;background:#191b20}}.variant>summary{{padding:12px}}.chosen{{color:var(--gold);font-size:12px;flex:0 0 auto}}.angle{{padding:0 12px;color:var(--muted);font-size:14px}}
.copy-field{{margin:12px;border:1px solid var(--line);border-radius:12px;overflow:hidden;min-width:0}}.field-head{{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:8px 10px;background:#202228}}.field-head h3{{font-size:14px;margin:0}}button.copy{{margin:0;padding:8px 11px;font-size:13px;white-space:nowrap}}pre{{margin:0;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word;font:14px/1.55 ui-monospace,monospace;max-height:420px;overflow:auto;background:#101114}}.all-fields{{margin:12px;padding:0}}.all-fields>summary{{font-size:13px;padding:10px 12px}}.all-copy{{margin:0 12px 12px!important}}#toast{{position:fixed;z-index:30;left:50%;bottom:18px;transform:translate(-50%,20px);opacity:0;pointer-events:none;background:#e8b96a;color:#181511;padding:10px 16px;border-radius:12px;font-weight:650;transition:.18s;max-width:calc(100vw - 24px);text-align:center}}#toast.visible{{opacity:1;transform:translate(-50%,0)}}button:disabled{{opacity:.65;cursor:wait}}
.publish-card{{margin-top:16px}}.youtube-download{{margin:8px 12px 4px}}.youtube-intro{{margin:12px 12px 4px}}.youtube-field{{margin-top:10px;margin-bottom:10px}}.draft-hint{{margin:0 12px 12px}}
@media(max-width:560px){{body{{padding:10px}}main{{border-radius:16px;padding:18px 14px}}.workspace{{margin-top:22px;padding-top:18px}}.workspace h2{{font-size:19px}}.song>summary{{flex-wrap:wrap}}.song-stage{{text-align:left}}.variants{{padding:0 8px 8px}}.variant>summary{{padding:11px 10px}}.copy-field{{margin:10px 8px}}.field-head{{align-items:flex-start;flex-wrap:wrap}}.field-head button{{min-height:40px}}.all-fields,.all-copy{{margin-left:8px!important;margin-right:8px!important}}pre{{font-size:13px;max-height:360px}}}}
.send-row{{margin:0 12px}}.send-suno[hidden]{{display:none}}.send-suno{{margin:4px 0 8px}}
</style></head><body><main><div class="eyebrow">Sovigen · локально</div><h1>Студия песни</h1><p class="intro">Тексты и настройки вариантов для Suno — рядом, с копированием каждого поля. Ниже — сборка готового трека в YouTube-видео.</p>
{notice}<section class="workspace"><h2>Загрузить трек и обложку</h2><p class="section-intro">Загрузки появляются по мере готовности песни.</p>{upload_section}</section>
<section class="workspace" id="youtube-publish"><h2>Подготовка к YouTube</h2><p class="section-intro">Сначала скачай видео, затем скопируй заголовок, описание и теги по шагам.</p>{youtube_section}</section>
<section class="workspace"><h2>Подготовка в Suno</h2><p class="section-intro">Открой вариант, скопируй Lyrics, Style и Exclude Styles по отдельности и вставь в соответствующие поля Suno.</p>{suno_section}</section>
<section class="workspace builder"><h2>Сборка видео</h2>{download}{form}</section></main>
<div id="toast" role="status" aria-live="polite"></div>
<script>
document.querySelectorAll('form').forEach(form=>form.addEventListener('submit',()=>{{const b=form.querySelector('button[type="submit"]');if(b){{b.disabled=true;b.textContent='Загружаю и собираю…'}}}}));
document.querySelectorAll('[data-copy]').forEach(button=>button.addEventListener('click',async()=>{{
  const target=document.getElementById(button.dataset.copy);if(!target)return;const value=target.textContent.trim();let copied=false;
  try{{if(navigator.clipboard?.writeText){{await navigator.clipboard.writeText(value);copied=true}}}}catch{{}}
  const toast=document.getElementById('toast');
  if(!copied){{const field=document.createElement('textarea');field.value=value;field.setAttribute('readonly','');field.setAttribute('aria-label','Текст для ручного копирования');field.style.cssText='position:fixed;z-index:20;left:12px;right:12px;bottom:72px;width:calc(100% - 24px);height:150px;background:#191b20;color:#fff;border:2px solid #e8b96a;border-radius:12px;padding:12px;font:13px/1.45 monospace;opacity:1';document.body.appendChild(field);field.focus();field.select();try{{copied=document.execCommand('copy')}}catch{{}}if(copied)field.remove();else{{toast.textContent='Выдели текст в появившемся окне и скопируй';toast.classList.add('visible');setTimeout(()=>{{toast.classList.remove('visible');field.remove()}},12000);return}}}}
  toast.textContent=copied?'Скопировано':'Скопировать не удалось';toast.classList.add('visible');setTimeout(()=>toast.classList.remove('visible'),2600)
}}));
const sendButtons=document.querySelectorAll('.send-suno');
if(sendButtons.length){{
  const refresh=()=>fetch('/api/suno/status').then(r=>r.json()).then(s=>sendButtons.forEach(b=>{{if(!b.dataset.busy)b.hidden=!s.available}})).catch(()=>sendButtons.forEach(b=>{{b.hidden=true}}));
  refresh();setInterval(refresh,5000);
  sendButtons.forEach(button=>button.addEventListener('click',async()=>{{
    const toast=document.getElementById('toast');const label=button.textContent;
    button.disabled=true;button.dataset.busy='1';button.textContent='Отправляю в Suno…';
    let text='Не удалось отправить';
    try{{
      const response=await fetch('/api/suno/send',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{slug:button.dataset.slug,variant:button.dataset.variant}})}});
      const result=await response.json();
      text=result.ok?`Suno запущен: ${{result.clips}} клипа`:`Ошибка: ${{result.error}}`;
    }}catch{{}}
    button.disabled=false;delete button.dataset.busy;button.textContent=label;
    toast.textContent=text;toast.classList.add('visible');setTimeout(()=>toast.classList.remove('visible'),6000);
  }}));
}}
</script></body></html>"""
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
        route = urlparse(self.path).path
        if route == "/api/suno/send":
            self._suno_send()
            return
        if route not in {"/record-track", "/record-cover", "/build"}:
            self._send_html(_page("Страница не найдена."), 404)
            return
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
                    message = f"Трек загружен для варианта {variant_id.upper()}; песня перешла на этап recorded. Ниже появилась загрузка обложки."
                    self._send_html(_page(message))
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
                    message = "Обложка загружена; песня готова к сборке. Проверь YouTube-заголовок и описание перед релизом."
                    self._send_html(_page(message))
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
            self._send_html(_page(download_slug=slug))
        except (ValueError, commands.CommandError) as err:
            self._send_html(_page(str(err)), 400)
        except Exception as err:
            self._send_html(_page(f"Не удалось собрать видео: {err}"), 500)


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
