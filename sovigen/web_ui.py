"""HTML for the studio: pure functions from prepared data to markup."""

from html import escape
from urllib.parse import quote

from . import youtube

STAGE_RU = {
    "idea": "Идея",
    "brief": "Бриф",
    "lyrics": "Текст",
    "prompted": "Suno",
    "recorded": "Трек",
    "ready": "Видео",
    "pre-published": "YouTube",
    "published": "Готово",
}
NEXT_RU = {
    "idea": "Ждёт Claude",
    "brief": "Ждёт Claude",
    "lyrics": "Ждёт Claude",
    "prompted": "Сгенерировать в Suno",
    "recorded": "Загрузить обложку",
    "ready": "Собрать видео",
    "pre-published": "Загрузить на YouTube",
    "published": "Опубликовано",
}
GROUPS = (
    ("Ваш ход", "you"),
    ("Ход Claude", "claude"),
    ("Опубликовано", "-"),
)

CSS = """
:root{--night:#10111A;--side:#0C0D14;--panel:#181A26;--raise:#222538;--line:#2E3248;--chalk:#ECEBF6;--muted:#9496B0;--signal:#8B93FF;--signal-d:#6F78F2;--ok:#59E0A0;--warn:#FFB454;--bad:#FF7A7A;--display:'Unbounded',system-ui,sans-serif;--ui:'Golos Text',system-ui,sans-serif}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--night);color:var(--chalk);font:16px/1.5 var(--ui)}
button,input,select,textarea{font:inherit;color:inherit}button{cursor:pointer}
:focus-visible{outline:3px solid var(--signal);outline-offset:2px}
a{color:var(--signal)}
.shell{display:grid;grid-template-columns:272px minmax(0,1fr);min-height:100vh}
.side{position:sticky;top:0;height:100vh;overflow:auto;display:flex;flex-direction:column;background:var(--side);border-right:1px solid var(--line);padding:20px 12px 14px}
.side-top{display:flex;align-items:center;justify-content:space-between;padding:0 8px 18px}
.logo{font:700 15px var(--display);letter-spacing:-.01em}
.close{display:none;background:none;border:0;font-size:28px;line-height:1;color:var(--muted)}
.grp{margin:0 0 18px}.grp h2{font:600 12.5px var(--ui);color:var(--muted);margin:0 8px 6px}
.sg{display:grid;grid-template-columns:auto 1fr;gap:1px 10px;width:100%;text-align:left;text-decoration:none;color:inherit;border-radius:10px;padding:9px 8px}
.sg:hover{background:#171926}.sg[aria-current=page]{background:var(--raise)}
.sg i{width:8px;height:8px;border-radius:50%;margin-top:8px;background:var(--line)}
.sg i.you{background:var(--signal)}.sg i.claude{background:var(--warn)}.sg i.done{background:var(--ok);opacity:.6}
.sg b{font-weight:600;font-size:15px;line-height:1.3}.sg small{grid-column:2;color:var(--muted);font-size:12.5px}
.side-foot{margin-top:auto;padding:12px 8px 0}
.pill{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-size:13px;color:var(--muted);background:var(--panel)}
.pill i{width:8px;height:8px;border-radius:50%;background:var(--line)}
.pill.on{color:var(--chalk)}.pill.on i{background:var(--ok);box-shadow:0 0 0 4px #59E0A022}
.main{min-width:0}.mbar{display:none}.scrim{display:none}
.wrap{padding:28px clamp(16px,3vw,44px) 140px;max-width:1180px}
.head{margin:0 0 20px}
.head h1{font:700 clamp(24px,4.6vw,44px)/1.1 var(--display);letter-spacing:-.025em;margin:0;text-wrap:balance}
.head p{margin:10px 0 0;color:var(--muted);max-width:64ch}
.notice{margin:0 0 18px;padding:14px 16px;border-radius:12px;border:1px solid #6e5d35;background:#2b261c}
.notice.ok{border-color:#2f6a4c;background:#16281f}.notice.bad{border-color:#7b3a3a;background:#2a1717}
.strips{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.strip{display:flex;flex-direction:column;background:var(--panel);border:1px solid var(--line);border-radius:18px;overflow:hidden;min-width:0}
.strip-h{display:flex;align-items:center;gap:14px;padding:16px 16px 12px}
.letter{font:700 44px/1 var(--display);color:var(--signal);width:48px}
.strip-h b{display:block;font-weight:600}.strip-h small{color:var(--muted);font-size:13px;display:block;line-height:1.35}
.strip-body{padding:0 12px 12px;display:grid;gap:8px;flex:1;align-content:start}
details.f{background:var(--night);border:1px solid var(--line);border-radius:12px}
details.f summary{list-style:none;display:grid;grid-template-columns:1fr auto 18px;align-items:center;gap:8px;padding:10px 12px;cursor:pointer;font-weight:500;font-size:15px}
details.f summary::-webkit-details-marker{display:none}
details.f summary:after{content:'+';color:var(--muted)}details.f[open] summary:after{content:'−'}
details.f pre,.field pre{margin:0;padding:0 12px 12px;white-space:pre-wrap;overflow-wrap:anywhere;font:13.5px/1.65 var(--ui);color:#D6D5E8;max-height:260px;overflow:auto}
.copy{background:var(--raise);border:0;border-radius:8px;padding:5px 10px;font-size:13px}.copy:hover{background:#2e3250}
.strip-f{padding:12px}.hint{font-size:12.5px;color:var(--muted);margin:8px 2px 0}
.btn,a.btn{display:inline-flex;align-items:center;justify-content:center;width:100%;min-height:50px;padding:0 18px;border-radius:12px;border:1px solid var(--line);background:var(--raise);font-weight:600;text-decoration:none;color:var(--chalk)}
.btn.primary,a.btn.primary{background:var(--signal);border-color:var(--signal);color:#0c0d18}.btn.primary:hover{background:var(--signal-d)}
.btn[disabled]{opacity:.55;cursor:wait}.btn.inline{width:auto}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:clamp(16px,3vw,28px);max-width:760px;margin-top:18px}
.panel:first-child{margin-top:0}
.panel h2{font:700 20px/1.25 var(--display);margin:0 0 8px;letter-spacing:-.01em}.panel>p{color:var(--muted);margin:0 0 18px}
.rows{display:grid;gap:8px}
.r{display:flex;align-items:center;justify-content:space-between;gap:12px;background:var(--night);border:1px solid var(--line);border-radius:12px;padding:12px 14px}
.r div{min-width:0}.r small{display:block;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.r .copy{flex:0 0 auto}
.field{background:var(--night);border:1px solid var(--line);border-radius:12px;margin-top:8px;overflow:hidden}
.field header{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 12px;font-weight:500;font-size:15px}
.form{display:grid;gap:12px}
label.lbl{display:grid;gap:6px;font-weight:600;font-size:14px}
input[type=url],input[type=text],select{width:100%;min-height:48px;border-radius:12px;border:1px solid var(--line);background:var(--night);padding:0 14px}
.drop{display:block;border:2px dashed #41466b;border-radius:14px;padding:18px;text-align:center;color:var(--muted)}
.drop b{display:block;color:var(--chalk);font-size:16px}.drop input{margin-top:10px;max-width:100%;color:var(--muted)}.drop input::file-selector-button{margin-right:12px;border:0;border-radius:8px;padding:8px 14px;background:var(--raise);color:var(--chalk);font:600 14px var(--ui);cursor:pointer}.drop input::file-selector-button:hover{background:#2e3250}
.video{position:relative;width:100%;aspect-ratio:16/9;border-radius:14px;overflow:hidden;background:#000;border:1px solid var(--line)}
.video iframe{position:absolute;inset:0;width:100%;height:100%;border:0}
.meta{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin-top:12px;color:var(--muted);font-size:14px}
details.edit{margin-top:14px}details.edit summary{cursor:pointer;color:var(--muted);font-size:14px}details.edit .form{margin-top:10px}
.send-row{display:flex;flex-wrap:wrap;gap:8px}.send-suno[hidden]{display:none}
.segs{display:none}
.toast{position:fixed;left:50%;bottom:90px;transform:translate(-50%,16px);background:var(--chalk);color:#10111A;padding:11px 18px;border-radius:12px;font-weight:600;opacity:0;pointer-events:none;transition:.2s;z-index:50;max-width:calc(100vw - 24px);text-align:center}
.toast.on{opacity:1;transform:translate(-50%,0)}
.sendall{display:none}
@media (max-width:980px){
 .shell{display:block}
 .side{position:fixed;z-index:40;left:0;top:0;bottom:0;width:min(330px,88vw);transform:translateX(-102%);transition:transform .22s}
 body.nav .side{transform:none}body.nav .scrim{display:block;position:fixed;inset:0;background:#000a;z-index:35}
 .close{display:block}
 .mbar{display:flex;align-items:center;gap:12px;position:sticky;top:0;z-index:10;background:var(--night);border-bottom:1px solid var(--line);padding:10px 14px}
 .mbar button{background:var(--panel);border:1px solid var(--line);border-radius:10px;width:42px;height:42px;font-size:20px}
 .mbar b{flex:1;font:600 15px var(--ui);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
 .wrap{padding-top:18px}
 .strips{grid-template-columns:1fr}
 .segs{display:flex;gap:6px;margin:0 0 14px;background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:4px}
 .segs button{flex:1;min-height:44px;border:0;background:transparent;border-radius:10px;font:600 15px var(--display)}
 .segs button[aria-selected=true]{background:var(--signal);color:#0c0d18}
 .strip:not(.active){display:none}.strip-f .send-suno{display:none}
 .sendall{display:block;position:fixed;left:0;right:0;bottom:0;padding:22px 16px 16px;background:linear-gradient(transparent,var(--night) 35%);z-index:20}
 .toast{bottom:96px}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

JS = """
const $=s=>document.querySelector(s);
const toast=t=>{const e=$('#toast');e.textContent=t;e.classList.add('on');clearTimeout(toast.t);toast.t=setTimeout(()=>e.classList.remove('on'),2600)};
async function copyText(value){
  let ok=false;
  try{if(navigator.clipboard?.writeText){await navigator.clipboard.writeText(value);ok=true}}catch{}
  if(!ok){const f=document.createElement('textarea');f.value=value;f.setAttribute('readonly','');f.style.cssText='position:fixed;left:12px;right:12px;bottom:72px;width:calc(100% - 24px);height:150px;z-index:60;background:#181A26;color:#fff;border:2px solid #8B93FF;border-radius:12px;padding:12px';document.body.appendChild(f);f.focus();f.select();try{ok=document.execCommand('copy')}catch{}
    if(ok)f.remove();else{toast('Выдели текст и скопируй');setTimeout(()=>f.remove(),12000);return}}
  toast('Скопировано')}
document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',e=>{e.preventDefault();e.stopPropagation();const t=document.getElementById(b.dataset.copy);if(t)copyText(t.textContent.trim())}));
$('#open')?.addEventListener('click',()=>document.body.classList.add('nav'));
[$('#close'),$('#scrim')].forEach(el=>el?.addEventListener('click',()=>document.body.classList.remove('nav')));
document.querySelectorAll('form').forEach(f=>f.addEventListener('submit',()=>{const b=f.querySelector('button[type=submit]');if(b){b.disabled=true;b.textContent='Подожди…'}}));
const strips=[...document.querySelectorAll('.strip')];
document.querySelectorAll('.segs button').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('.segs button').forEach(x=>x.setAttribute('aria-selected',x===b));
  strips.forEach(s=>s.classList.toggle('active',s.dataset.v===b.dataset.v));
  document.querySelectorAll('.sendall .send-suno').forEach(x=>{x.dataset.variant=b.dataset.v;x.textContent='Отправить '+b.dataset.v.toUpperCase()+' в Suno'});
}));
const sendButtons=[...document.querySelectorAll('.send-suno')];
function setPill(on){document.querySelectorAll('.suno-pill').forEach(p=>{p.classList.toggle('on',on);p.querySelector('span').textContent=on?'Suno на связи':'Только копирование'})}
async function refresh(){let on=false;try{on=(await (await fetch('/api/suno/status')).json()).available}catch{}
  setPill(on);sendButtons.forEach(b=>{if(!b.dataset.busy)b.hidden=!on})}
refresh();setInterval(refresh,5000);
sendButtons.forEach(button=>button.addEventListener('click',async()=>{
  const label=button.textContent;sendButtons.forEach(b=>{b.disabled=true;b.dataset.busy='1'});button.textContent='Отправляю в Suno…';
  let text='Не удалось отправить';
  try{const r=await fetch('/api/suno/send',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({slug:button.dataset.slug,variant:button.dataset.variant})});
    const res=await r.json();text=res.ok?`Suno запущен: ${res.clips} клипа`:`Ошибка: ${res.error}`}catch{}
  sendButtons.forEach(b=>{b.disabled=false;delete b.dataset.busy});button.textContent=label;toast(text);refresh()}));
"""

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link href="https://fonts.googleapis.com/css2?family=Unbounded:wght@500;700&'
    'family=Golos+Text:wght@400;500;600&display=swap" rel="stylesheet">'
)


def _e(value) -> str:
    return escape(str(value), quote=True)


def _sidebar(songs: list, selected_slug) -> str:
    sections = []
    for label, turn in GROUPS:
        items = [song for song in songs if song["turn"] == turn]
        if not items:
            continue
        buttons = []
        for song in items:
            current = ' aria-current="page"' if song["slug"] == selected_slug else ""
            dot = {"you": "you", "claude": "claude"}.get(turn, "done")
            sub = NEXT_RU.get(song["stage"], song["stage"])
            buttons.append(
                f'<a class="sg" href="/?song={quote(song["slug"], safe="")}"{current}>'
                f'<i class="{dot}"></i><b>{_e(song["title"])}</b><small>{_e(sub)}</small></a>'
            )
        sections.append(f'<section class="grp"><h2>{label}</h2>{"".join(buttons)}</section>')
    return "".join(sections) or '<p class="hint" style="padding:0 8px">Песен пока нет.</p>'


def _copy_field(label: str, text: str, field_id: str) -> str:
    return (
        f'<div class="field"><header>{_e(label)}'
        f'<button class="copy" type="button" data-copy="{field_id}">Копировать</button></header>'
        f'<pre id="{field_id}">{escape(text)}</pre></div>'
    )


def _suno_panel(song: dict) -> str:
    variants = song["variants"]
    first = variants[0]["id"] if variants else ""
    segs = "".join(
        f'<button type="button" role="tab" data-v="{_e(v["id"])}" aria-selected="{str(v["id"] == first).lower()}">'
        f'{_e(v["id"].upper())}</button>'
        for v in variants
    )
    strips = []
    for number, variant in enumerate(variants, 1):
        vid = variant["id"]
        parts = []
        for key, label in (("lyrics", "Текст"), ("style", "Style"), ("exclude", "Exclude")):
            field_id = f"{key}-{number}"
            parts.append(
                f'<details class="f"><summary>{label}'
                f'<button class="copy" type="button" data-copy="{field_id}">Копировать</button></summary>'
                f'<pre id="{field_id}">{escape(variant[key])}</pre></details>'
            )
        if variant["guidance"]:
            parts.append(
                f'<details class="f"><summary>Заметки'
                f'<button class="copy" type="button" data-copy="guidance-{number}">Копировать</button></summary>'
                f'<pre id="guidance-{number}">{escape(variant["guidance"])}</pre></details>'
            )
        chosen = "Выбран · " if variant["chosen"] else ""
        strips.append(
            f'<article class="strip{" active" if vid == first else ""}" data-v="{_e(vid)}">'
            f'<div class="strip-h"><span class="letter">{_e(vid.upper())}</span><div>'
            f'<b>{chosen}{_e(variant["card"])}</b><small>{_e(variant["angle"])}</small></div></div>'
            f'<div class="strip-body">{"".join(parts)}</div>'
            f'<div class="strip-f"><button class="btn primary send-suno" type="button" hidden '
            f'data-slug="{_e(song["slug"])}" data-variant="{_e(vid)}">Отправить {_e(vid.upper())} в Suno</button></div></article>'
        )
    sendall = (
        f'<div class="sendall"><button class="btn primary send-suno" type="button" hidden '
        f'data-slug="{_e(song["slug"])}" data-variant="{_e(first)}">Отправить {_e(first.upper())} в Suno</button></div>'
    )
    options = "".join(
        f'<option value="{_e(v["id"])}"{" selected" if v["chosen"] else ""}>'
        f'{_e(v["id"].upper())} · {_e(v["card"])}</option>'
        for v in variants
    )
    placeholder = "" if any(v["chosen"] for v in variants) else '<option value="" disabled selected>Выбери вариант записи</option>'
    upload = f"""<section class="panel"><h2>Загрузить трек</h2>
      <p>После генерации выбери вариант, по которому записан трек, и загрузи файл.</p>
      <form class="form" action="/record-track" method="post" enctype="multipart/form-data">
        <input type="hidden" name="slug" value="{_e(song["slug"])}">
        <label class="lbl">Вариант<select name="variant" required>{placeholder}{options}</select></label>
        <label class="drop"><b>MP3, M4A или WAV</b>до 160 МБ<input name="audio" type="file" accept=".mp3,.m4a,.wav,audio/*" required></label>
        <button class="btn primary" type="submit">Загрузить трек</button></form></section>"""
    return (
        f'<div class="segs" role="tablist">{segs}</div><div class="strips">{"".join(strips)}</div>'
        f"{sendall}{upload}"
    )


def _cover_panel(song: dict) -> str:
    return f"""<section class="panel"><h2>Загрузить обложку</h2>
      <p>Трек загружен. Добавь обложку, чтобы перейти к сборке видео. Перед сборкой проверь, что YouTube-заголовок и описание готовы.</p>
      <form class="form" action="/record-cover" method="post" enctype="multipart/form-data">
        <input type="hidden" name="slug" value="{_e(song["slug"])}">
        <label class="drop"><b>JPG, PNG или WebP</b>до 160 МБ<input name="cover" type="file" accept=".jpg,.jpeg,.png,.webp,image/*" required></label>
        <button class="btn primary" type="submit">Загрузить обложку</button></form></section>"""


def _build_panel(song: dict) -> str:
    return f"""<section class="panel"><h2>Собрать видео</h2>
      <p>Видео собирается со статичной обложкой. Уже загруженные файлы используются автоматически.</p>
      <form class="form" action="/build" method="post" enctype="multipart/form-data">
        <input type="hidden" name="slug" value="{_e(song["slug"])}">
        <label class="drop"><b>Финальный трек</b>MP3, M4A или WAV — если ещё не загружен<input name="audio" type="file" accept=".mp3,.m4a,.wav,audio/*"></label>
        <label class="drop"><b>Обложка</b>JPG, PNG или WebP — если ещё не загружена<input name="cover" type="file" accept=".jpg,.jpeg,.png,.webp,image/*"></label>
        <button class="btn primary" type="submit">Собрать видео</button></form></section>"""


def _publish_panel(song: dict) -> str:
    fields = song["youtube"]
    rows = []
    for name, label in (("title", "Заголовок"), ("description", "Описание"), ("tags", "Теги")):
        if fields.get(name):
            rows.append(_copy_field(label, fields[name], f"yt-{name}"))
    draft = '<p class="hint">Список тегов — черновое предложение; проверь его перед публикацией.</p>' if fields.get("tags_draft") else ""
    if song.get("video_mb") is None:
        download = '<p class="hint">Файла youtube.mp4 нет в этой копии проекта: медиа не хранятся в git. Собранное видео лежит на машине, где оно собиралось.</p>'
    else:
        download = (
            f'<a class="btn primary inline" href="/download/{quote(song["slug"], safe="")}">'
            f'Скачать видео · {song["video_mb"]:.1f} МБ</a>'
        )
    return f"""<section class="panel"><h2>Загрузить на YouTube</h2>
      <p>Загрузи видео на YouTube и скопируй поля по порядку.</p>
      {download}
      {"".join(rows)}{draft}</section>
      <section class="panel"><h2>Опубликовано?</h2>
      <p>Вставь ссылку на видео. Она сохранится в проекте, а видео откроется здесь.</p>
      <form class="form" action="/publish" method="post" enctype="multipart/form-data">
        <input type="hidden" name="slug" value="{_e(song["slug"])}">
        <label class="lbl">Ссылка на YouTube<input type="url" name="url" placeholder="https://youtu.be/…"></label>
        <button class="btn primary" type="submit">Отметить опубликованным</button></form></section>"""


def _published_panel(song: dict) -> str:
    link = song.get("youtube_url")
    vid = youtube.video_id(link) if link else None
    if vid:
        player = (
            f'<div class="video"><iframe src="{_e(youtube.embed_url(vid))}" title="{_e(song["title"])}" '
            'loading="lazy" referrerpolicy="strict-origin-when-cross-origin" '
            'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe></div>'
            f'<div class="meta"><a href="{_e(link)}" target="_blank" rel="noopener">Открыть на YouTube</a></div>'
        )
        edit_label = "Изменить ссылку"
    else:
        player = '<p class="hint">Ссылка на видео пока не сохранена.</p>'
        edit_label = "Добавить ссылку"
    return f"""<section class="panel" style="max-width:900px"><h2>Результат</h2>{player}
      <details class="edit"{"" if vid else " open"}><summary>{edit_label}</summary>
      <form class="form" action="/youtube" method="post" enctype="multipart/form-data">
        <input type="hidden" name="slug" value="{_e(song["slug"])}">
        <label class="lbl">Ссылка на YouTube<input type="url" name="url" required value="{_e(link or "")}" placeholder="https://youtu.be/…"></label>
        <button class="btn" type="submit">Сохранить ссылку</button></form></details></section>"""


def _detail(song: dict) -> str:
    stage = song["stage"]
    index = list(STAGE_RU).index(stage) + 1 if stage in STAGE_RU else 0
    intro = f'{STAGE_RU.get(stage, stage)} · шаг {index} из {len(STAGE_RU)} · {NEXT_RU.get(stage, "")}'
    if stage == "prompted" and song["variants"]:
        body = _suno_panel(song)
    elif stage == "recorded":
        body = _cover_panel(song)
    elif stage == "ready":
        body = _build_panel(song)
    elif stage == "pre-published":
        body = _publish_panel(song)
    elif stage == "published":
        body = _published_panel(song)
    else:
        body = '<section class="panel"><h2>Ждёт Claude</h2><p>Бриф, тексты и промпты для Suno готовит Claude. Песня появится здесь на стадии Suno.</p></section>'
    takes = f" · клипов в Suno: {song['takes']}" if song.get("takes") else ""
    return f'<div class="head"><h1>{_e(song["title"])}</h1><p>{_e(intro)}{_e(takes)}</p></div>{body}'


def render_page(state: dict) -> bytes:
    selected = state["selected"]
    notice = ""
    if state.get("message"):
        kind = state.get("kind", "")
        notice = f'<div class="notice {kind}" role="status">{escape(state["message"])}</div>'
    detail = _detail(selected) if selected else '<div class="head"><h1>Студия песен</h1><p>Выбери песню слева.</p></div>'
    selected_slug = selected["slug"] if selected else None
    title = selected["title"] if selected else "Студия"
    pill = '<span class="pill suno-pill"><i></i><span>Только копирование</span></span>'
    document = f"""<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sovigen · {_e(title)}</title>{FONTS}<style>{CSS}</style></head>
<body><div class="shell">
<aside class="side" aria-label="Песни"><div class="side-top"><span class="logo">sovigen</span><button class="close" id="close" type="button" aria-label="Закрыть список">×</button></div>
<nav>{_sidebar(state["songs"], selected_slug)}</nav><div class="side-foot">{pill}</div></aside>
<div class="scrim" id="scrim"></div>
<div class="main"><div class="mbar"><button id="open" type="button" aria-label="Открыть список песен">☰</button><b>{_e(title)}</b>{pill}</div>
<div class="wrap">{notice}{detail}</div></div></div>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<script>{JS}</script></body></html>"""
    return document.encode("utf-8")
