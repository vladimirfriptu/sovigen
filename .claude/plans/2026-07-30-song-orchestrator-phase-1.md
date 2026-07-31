# План реализации: оркестратор песен, фаза 1

> **Для агентов:** ОБЯЗАТЕЛЬНЫЙ СУБ-СКИЛЛ: используй
> `superpowers:subagent-driven-development` (рекомендуется) или
> `superpowers:executing-plans`, чтобы исполнять план задача за задачей.
> Шаги отмечаются чекбоксами `- [ ]`.

**Цель:** довести sovigen до состояния, когда песню можно провести от замысла
до готового Suno-промпта целиком внутри проекта, а состояние переживает конец
сессии.

**Архитектура:** CLI владеет детерминированным (папки, шаблоны артефактов,
переходы стадий с проверкой файлов, раскладка скачанных файлов); творческие
этапы — скиллы Claude, читающие общую базу знаний `knowledge/`. Состояние
песни — `meta.json` схемы версии 2 в её папке.

**Стек:** Python 3.9+, только стандартная библиотека; ffmpeg/ffprobe; pytest
для тестов; `just` как обёртка.

## Глобальные ограничения

- Внешних Python-зависимостей не добавлять: только стандартная библиотека.
  Системные зависимости — `python3` и `ffmpeg`/`ffprobe` в PATH.
- Тесты — на чистом Python (`pytest`), в существующем стиле `tests/`: фикстура
  `lib` через `monkeypatch.setenv("SOVIGEN_LIBRARY", ...)` и `tmp_path`.
- Все тексты, видимые пользователю в CLI, — на английском (как сейчас).
  Содержимое `knowledge/` и шаблонов артефактов — на русском/украинском.
- Файлы, обращённые к Claude (скиллы, `knowledge/README.md`), пишутся
  по-английски там, где это инструкция; предметное содержание (правила
  переспіву, карточки стилей) остаётся на русском.
- Репозиторий публичный: никаких ключей и токенов в файлах.
- Коммиты — по-английски, без co-author трейлера.
- Не трогать существующие песни в `library/`: миграция происходит на чтение,
  файлы не переписываются задним числом.

---

## Структура файлов

Создаются:

- `sovigen/artifacts.py` — шаблоны артефактов и требования стадий к файлам.
  Единственный модуль, который знает про имена md-файлов.
- `sovigen/templates/*.md` — заготовки артефактов песни.
- `knowledge/**` — база знаний (см. задачи 8–9).
- `.claude/skills/song*/SKILL.md` — скиллы (задачи 10–11).

Изменяются:

- `sovigen/meta.py` — схема v2, восемь стадий, `stage_history`. Знает про
  состояние, не знает про файлы артефактов.
- `sovigen/commands.py` — `new` через шаблоны, новые `advance` и `import`,
  расширенный `status`.
- `sovigen/cli.py` — новые подкоманды и `--json`.
- `.gitignore`, `justfile`, `README.md`.

Границы: `meta.py` ничего не знает о существовании `brief.md`; `artifacts.py`
ничего не знает о переходах стадий. Связывает их `commands.py`.

---

### Задача 1: схема meta v2 и восемь стадий

**Файлы:**
- Изменить: `sovigen/meta.py`
- Тест: `tests/test_meta.py`

**Интерфейсы:**
- Производит: `STAGES: list[str]`, `META_VERSION = 2`,
  `new_meta(title, slug, created, *, source=None, series=None, language="uk") -> dict`,
  `read_meta(song_dir) -> dict` (нормализует старую схему),
  `write_meta(song_dir, data) -> None`,
  `set_stage(song_dir, stage, at) -> None`,
  `next_stage(stage) -> str | None`.

- [ ] **Шаг 1: написать падающие тесты**

Добавить в `tests/test_meta.py`:

```python
def test_new_meta_shape():
    data = meta.new_meta("My Song", "my-song", "2026-07-30")
    assert data == {
        "meta_version": 2,
        "title": "My Song",
        "slug": "my-song",
        "stage": "idea",
        "created": "2026-07-30",
        "source": None,
        "series": None,
        "language": "uk",
        "style": None,
        "suno_takes": 0,
        "stage_history": [{"stage": "idea", "at": "2026-07-30"}],
    }


def test_read_normalizes_v1_draft_to_idea(tmp_path):
    legacy = {"title": "X", "slug": "x", "stage": "draft", "created": "2026-06-22"}
    (tmp_path / "meta.json").write_text(json.dumps(legacy), encoding="utf-8")
    data = meta.read_meta(tmp_path)
    assert data["stage"] == "idea"
    assert data["meta_version"] == 2
    assert data["stage_history"] == []


def test_read_keeps_v1_published_stage(tmp_path):
    legacy = {"title": "X", "slug": "x", "stage": "published", "created": "2026-06-22"}
    (tmp_path / "meta.json").write_text(json.dumps(legacy), encoding="utf-8")
    assert meta.read_meta(tmp_path)["stage"] == "published"


def test_read_does_not_rewrite_file(tmp_path):
    legacy = {"title": "X", "slug": "x", "stage": "draft", "created": "2026-06-22"}
    path = tmp_path / "meta.json"
    path.write_text(json.dumps(legacy), encoding="utf-8")
    meta.read_meta(tmp_path)
    assert json.loads(path.read_text(encoding="utf-8")) == legacy


def test_set_stage_appends_history(tmp_path):
    meta.write_meta(tmp_path, meta.new_meta("X", "x", "2026-07-30"))
    meta.set_stage(tmp_path, "brief", "2026-07-31")
    data = meta.read_meta(tmp_path)
    assert data["stage"] == "brief"
    assert data["stage_history"][-1] == {"stage": "brief", "at": "2026-07-31"}


def test_set_stage_invalid(tmp_path):
    meta.write_meta(tmp_path, meta.new_meta("X", "x", "2026-07-30"))
    with pytest.raises(ValueError):
        meta.set_stage(tmp_path, "bogus", "2026-07-31")


def test_next_stage():
    assert meta.next_stage("idea") == "brief"
    assert meta.next_stage("ready") == "pre-published"
    assert meta.next_stage("published") is None
```

Добавить `import json` в начало файла теста. Старый `test_new_meta_shape`
заменить приведённым выше, старый `test_set_stage_valid` — на
`test_set_stage_appends_history`.

- [ ] **Шаг 2: убедиться, что тесты падают**

Запустить: `.venv/bin/python -m pytest tests/test_meta.py -v`
Ожидается: FAIL — `new_meta() got an unexpected keyword argument` и
несовпадение словаря.

- [ ] **Шаг 3: переписать `sovigen/meta.py`**

```python
import json
from pathlib import Path

META_VERSION = 2
META_FILENAME = "meta.json"

STAGES = [
    "idea",
    "brief",
    "lyrics",
    "prompted",
    "recorded",
    "ready",
    "pre-published",
    "published",
]

LEGACY_STAGES = {"draft": "idea"}


def new_meta(
    title: str,
    slug: str,
    created: str,
    *,
    source=None,
    series=None,
    language: str = "uk",
) -> dict:
    return {
        "meta_version": META_VERSION,
        "title": title,
        "slug": slug,
        "stage": "idea",
        "created": created,
        "source": source,
        "series": series,
        "language": language,
        "style": None,
        "suno_takes": 0,
        "stage_history": [{"stage": "idea", "at": created}],
    }


def meta_path(song_dir: Path) -> Path:
    return song_dir / META_FILENAME


def has_meta(song_dir: Path) -> bool:
    return meta_path(song_dir).exists()


def read_meta(song_dir: Path) -> dict:
    path = meta_path(song_dir)
    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    return _normalize(data)


def _normalize(data: dict) -> dict:
    # Файл на диске не переписываем: старые песни лежат как есть,
    # приведение к текущей схеме живёт только в памяти.
    normalized = dict(data)
    stage = normalized.get("stage")
    if stage in LEGACY_STAGES:
        normalized["stage"] = LEGACY_STAGES[stage]
    normalized.setdefault("source", None)
    normalized.setdefault("series", None)
    normalized.setdefault("language", "uk")
    normalized.setdefault("style", None)
    normalized.setdefault("suno_takes", 0)
    normalized.setdefault("stage_history", [])
    normalized["meta_version"] = META_VERSION
    return normalized


def write_meta(song_dir: Path, meta: dict) -> None:
    path = meta_path(song_dir)
    text = json.dumps(meta, ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8")


def set_stage(song_dir: Path, stage: str, at: str) -> None:
    if stage not in STAGES:
        raise ValueError(f"Unknown stage: {stage}")
    data = read_meta(song_dir)
    data["stage"] = stage
    data["stage_history"] = list(data["stage_history"]) + [{"stage": stage, "at": at}]
    write_meta(song_dir, data)


def next_stage(stage: str):
    index = STAGES.index(stage)
    if index + 1 >= len(STAGES):
        return None
    return STAGES[index + 1]
```

- [ ] **Шаг 4: прогнать тесты**

Запустить: `.venv/bin/python -m pytest tests/test_meta.py -v`
Ожидается: PASS. Остальной сьют пока красный — это чинится в задачах 3–6.

- [ ] **Шаг 5: коммит**

```bash
git add sovigen/meta.py tests/test_meta.py
git commit -m "Introduce meta schema v2 with eight stages and stage history"
```

---

### Задача 2: артефакты — шаблоны и требования стадий

**Файлы:**
- Создать: `sovigen/artifacts.py`
- Создать: `sovigen/templates/brief.md`, `lyrics.md`, `suno.md`,
  `cover-prompt.md`, `youtube.md`, `notes.md`
- Тест: `tests/test_artifacts.py`

**Интерфейсы:**
- Потребляет: ничего из задачи 1 (модуль независим).
- Производит: `ARTIFACT_FILES: list[str]`, `AUDIO`, `IMAGE` (маркеры),
  `STAGE_REQUIREMENTS: dict[str, list[str]]`,
  `render(song_dir, data) -> list[Path]`,
  `missing_for_stage(song_dir, stage) -> list[str]`.

- [ ] **Шаг 1: написать падающие тесты**

Создать `tests/test_artifacts.py`:

```python
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
```

- [ ] **Шаг 2: убедиться, что тесты падают**

Запустить: `.venv/bin/python -m pytest tests/test_artifacts.py -v`
Ожидается: FAIL — `ModuleNotFoundError: No module named 'sovigen.artifacts'`.

- [ ] **Шаг 3: создать шаблоны**

Шаблоны — обычные md с плейсхолдерами `{title}`, `{slug}`, `{source}`,
`{series}`, `{language}`, `{created}`, подставляемыми через `str.format_map`.

`sovigen/templates/brief.md`:

```markdown
---
song: {slug}
artifact: brief
source: {source}
series: {series}
language: {language}
---

# {title} — концепция

## Источник

<Что за текст лежит в основе, где сверен. Номера стихов — по еврейской нумерации.>

## О чём песня

<Две-три фразы: что здесь происходит с человеком.>

## Эмоциональная арка

<Откуда куда движется песня: от чего к чему.>

## Встроенные подарки текста

<Повторы, рефрены, готовые припевы — то, что структура источника даёт даром.>

## Стиль

Выбран: <ссылка вида [[styles/casting-crowns]]>

Почему: <одна-две фразы.>

Альтернативы:
- <вариант> — <чем отличается акцент>
- <вариант> — <чем отличается акцент>
```

`sovigen/templates/lyrics.md`:

```markdown
---
song: {slug}
artifact: lyrics
source: {source}
language: {language}
---

# {title} — текст

<Текст со структурными тегами: [Intro] [Verse] [Pre-Chorus] [Chorus] [Bridge]
[Outro], с пометками динамики вида [Verse 1: intimate], [Chorus: full band].
Без филлеров («о-о-о», «yeah», «на-на») — Suno их раздувает.>

## Соответствие источнику

| Секция | Стихи |
|---|---|
|  |  |

## Насколько близко к тексту

<Честно: что сжато, переставлено или опущено ради формата песни.>
```

`sovigen/templates/suno.md`:

```markdown
---
song: {slug}
artifact: suno
style: 
---

# {title} — генерация в Suno

## Style

```
<готовая строка на английском>
```

## Exclude Styles

```
<готовая строка на английском>
```

## Советы по генерации

<Что важно именно для этой песни: темп, размер, длина, чего ждать от вокала.>
```

`sovigen/templates/cover-prompt.md`:

```markdown
---
song: {slug}
artifact: cover-prompt
---

# {title} — промпт обложки

<Готовый промпт на английском: 16:9, 1920×1080, безопасные поля ~8% по краям,
без текста и логотипов. Общие правила — [[craft/cover]].>
```

`sovigen/templates/youtube.md`:

```markdown
---
song: {slug}
artifact: youtube
---

# {title} — публикация

## Заголовок

<Строка заголовка ролика.>

## Описание

<Текст описания.>

## Теги

<Через запятую.>
```

`sovigen/templates/notes.md`:

```markdown
---
song: {slug}
artifact: notes
created: {created}
---

# {title} — журнал

<Что делалось по ходу: сколько дублей в Suno, какие правки текста, что
сломалось. Отсюда `song-retro` берёт факты.>
```

- [ ] **Шаг 4: написать `sovigen/artifacts.py`**

```python
from pathlib import Path

AUDIO = "audio (.mp3)"
IMAGE = "image"

AUDIO_FILENAME = "track.mp3"
VIDEO_FILENAME = "youtube.mp4"

ARTIFACT_FILES = [
    "brief.md",
    "lyrics.md",
    "suno.md",
    "cover-prompt.md",
    "youtube.md",
    "notes.md",
]

STAGE_REQUIREMENTS = {
    "idea": [],
    "brief": ["brief.md"],
    "lyrics": ["lyrics.md"],
    "prompted": ["suno.md"],
    "recorded": [AUDIO],
    "ready": [IMAGE, "youtube.md"],
    "pre-published": [VIDEO_FILENAME],
    "published": [],
}

_TEMPLATES_DIR = Path(__file__).parent / "templates"


def render(song_dir: Path, data: dict) -> list:
    values = {
        "title": data.get("title", ""),
        "slug": data.get("slug", ""),
        "source": data.get("source") or "-",
        "series": data.get("series") or "-",
        "language": data.get("language") or "-",
        "created": data.get("created", ""),
    }
    created = []
    for name in ARTIFACT_FILES:
        target = song_dir / name
        if target.exists():
            continue
        template = (_TEMPLATES_DIR / name).read_text(encoding="utf-8")
        target.write_text(template.format_map(values), encoding="utf-8")
        created.append(target)
    return created


def missing_for_stage(song_dir: Path, stage: str) -> list:
    from .inputs import InputError, find_audio, find_image

    missing = []
    for requirement in STAGE_REQUIREMENTS.get(stage, []):
        if requirement == AUDIO:
            try:
                find_audio(song_dir)
            except InputError:
                missing.append(AUDIO)
            continue
        if requirement == IMAGE:
            try:
                find_image(song_dir)
            except InputError:
                missing.append(IMAGE)
            continue
        if not (song_dir / requirement).exists():
            missing.append(requirement)
    return missing
```

Внимание: шаблон `suno.md` содержит тройные бэктики и фигурные скобки не
содержит — но `str.format_map` падает на любых `{` в тексте. Проверить, что в
шаблонах нет одиночных фигурных скобок; если понадобятся, удваивать их (`{{`).

- [ ] **Шаг 5: прогнать тесты**

Запустить: `.venv/bin/python -m pytest tests/test_artifacts.py -v`
Ожидается: PASS.

- [ ] **Шаг 6: коммит**

```bash
git add sovigen/artifacts.py sovigen/templates tests/test_artifacts.py
git commit -m "Add artifact templates and per-stage file requirements"
```

---

### Задача 3: `new` раскладывает шаблоны

**Файлы:**
- Изменить: `sovigen/commands.py` (`cmd_new`)
- Тест: `tests/test_commands.py`

**Интерфейсы:**
- Потребляет: `meta.new_meta`, `artifacts.render`.
- Производит: `cmd_new(title, *, source=None, series=None, language="uk") -> Path`.

- [ ] **Шаг 1: написать падающие тесты**

Заменить в `tests/test_commands.py` тест `test_new_creates_structure` на:

```python
def test_new_creates_structure(lib):
    sdir = commands.cmd_new("Мій щит")
    assert (sdir / "raw").is_dir()
    assert (sdir / "meta.json").is_file()
    data = meta.read_meta(sdir)
    assert data["stage"] == "idea"
    assert data["meta_version"] == 2


def test_new_renders_artifacts(lib):
    sdir = commands.cmd_new("Мій щит")
    for name in ["brief.md", "lyrics.md", "suno.md", "cover-prompt.md",
                 "youtube.md", "notes.md"]:
        assert (sdir / name).is_file(), name


def test_new_records_source_and_series(lib):
    sdir = commands.cmd_new("Мій щит", source="psalm-3", series="psalms")
    data = meta.read_meta(sdir)
    assert data["source"] == "psalm-3"
    assert data["series"] == "psalms"
    assert "source: psalm-3" in (sdir / "brief.md").read_text(encoding="utf-8")
```

Также обновить хелпер `_make_song`: `stage="draft"` → `stage="idea"`.

- [ ] **Шаг 2: убедиться, что тесты падают**

Запустить: `.venv/bin/python -m pytest tests/test_commands.py -v`
Ожидается: FAIL — артефакты не создаются, `cmd_new` не принимает `source`.

- [ ] **Шаг 3: изменить `cmd_new`**

```python
def cmd_new(title: str, *, source=None, series=None, language: str = "uk") -> Path:
    slug = slugify(title)
    if not slug:
        raise CommandError(f"Could not derive a slug from title: {title!r}")
    sdir = paths.song_dir(slug)
    if sdir.exists():
        raise CommandError(f"Song already exists: {slug}")
    raw_dir = sdir / "raw"
    raw_dir.mkdir(parents=True)
    today = datetime.date.today().isoformat()
    data = meta_mod.new_meta(
        title, slug, today, source=source, series=series, language=language
    )
    meta_mod.write_meta(sdir, data)
    artifacts.render(sdir, data)
    return sdir
```

Добавить `from . import artifacts` в импорты модуля.

- [ ] **Шаг 4: прогнать тесты**

Запустить: `.venv/bin/python -m pytest tests/test_commands.py -v`
Ожидается: PASS для трёх тестов выше; тесты про `ready`/`build` могут падать —
их чинит задача 4.

- [ ] **Шаг 5: коммит**

```bash
git add sovigen/commands.py tests/test_commands.py
git commit -m "Scaffold song artifacts on new"
```

---

### Задача 4: `advance` — переход с проверкой файлов

**Файлы:**
- Изменить: `sovigen/commands.py` (добавить `cmd_advance`, удалить `cmd_ready`)
- Тест: `tests/test_commands.py`

**Интерфейсы:**
- Потребляет: `meta.next_stage`, `meta.set_stage`,
  `artifacts.missing_for_stage`.
- Производит: `cmd_advance(slug) -> tuple`, возвращает `(from_stage, to_stage)`;
  при отсутствии следующей стадии — `(stage, stage)`.

- [ ] **Шаг 1: написать падающие тесты**

```python
def test_advance_moves_to_next_stage(lib):
    sdir = _make_song(lib, "s", stage="idea", with_inputs=False)
    (sdir / "brief.md").write_text("x", encoding="utf-8")
    assert commands.cmd_advance("s") == ("idea", "brief")
    assert meta.read_meta(sdir)["stage"] == "brief"


def test_advance_refuses_without_required_file(lib):
    _make_song(lib, "s", stage="idea", with_inputs=False)
    with pytest.raises(commands.CommandError) as err:
        commands.cmd_advance("s")
    assert "missing: brief.md" in str(err.value)


def test_advance_at_final_stage_is_idempotent(lib):
    _make_song(lib, "s", stage="published", with_inputs=False)
    assert commands.cmd_advance("s") == ("published", "published")


def test_advance_records_history(lib):
    sdir = _make_song(lib, "s", stage="idea", with_inputs=False)
    (sdir / "brief.md").write_text("x", encoding="utf-8")
    commands.cmd_advance("s")
    history = meta.read_meta(sdir)["stage_history"]
    assert history[-1]["stage"] == "brief"
```

`_make_song` должен уметь ставить произвольную стадию — заменить в нём
`meta.set_stage(sdir, stage)` на `meta.set_stage(sdir, stage, "2026-07-30")`.

- [ ] **Шаг 2: убедиться, что тесты падают**

Запустить: `.venv/bin/python -m pytest tests/test_commands.py -k advance -v`
Ожидается: FAIL — `module 'sovigen.commands' has no attribute 'cmd_advance'`.

- [ ] **Шаг 3: реализовать**

```python
def cmd_advance(slug: str) -> tuple:
    sdir = _require_song(slug)
    data = meta_mod.read_meta(sdir)
    current = data["stage"]
    target = meta_mod.next_stage(current)
    if target is None:
        return (current, current)
    missing = artifacts.missing_for_stage(sdir, target)
    if missing:
        raise CommandError(f"cannot advance {slug} to {target}, missing: " + ", ".join(missing))
    today = datetime.date.today().isoformat()
    meta_mod.set_stage(sdir, target, today)
    return (current, target)
```

Удалить `cmd_ready` — его роль берёт `advance`. `cmd_publish` оставить: это
явное действие пользователя после заливки; переписать его на запись истории:

```python
def cmd_publish(slug: str) -> None:
    sdir = _require_song(slug)
    today = datetime.date.today().isoformat()
    meta_mod.set_stage(sdir, "published", today)
```

`cmd_build` тоже должен писать дату:
`meta_mod.set_stage(sdir, "pre-published", datetime.date.today().isoformat())`.

- [ ] **Шаг 4: прогнать весь сьют**

Запустить: `.venv/bin/python -m pytest -v`
Ожидается: падают только тесты CLI про `ready` — их чинит задача 6.

- [ ] **Шаг 5: коммит**

```bash
git add sovigen/commands.py tests/test_commands.py
git commit -m "Add advance command with per-stage file validation"
```

---

### Задача 5: `import` — раскладка скачанных файлов

**Файлы:**
- Изменить: `sovigen/commands.py`
- Тест: `tests/test_commands.py`

**Интерфейсы:**
- Производит: `cmd_import(slug, src) -> Path` — копирует файл в папку песни
  под каноническим именем и возвращает путь назначения.

- [ ] **Шаг 1: написать падающие тесты**

```python
def test_import_audio_to_canonical_name(lib, tmp_path):
    sdir = _make_song(lib, "s", stage="prompted", with_inputs=False)
    src = tmp_path / "Suno v5 take 3.mp3"
    src.write_bytes(b"audio")
    dest = commands.cmd_import("s", src)
    assert dest == sdir / "track.mp3"
    assert dest.read_bytes() == b"audio"


def test_import_keeps_source_file(lib, tmp_path):
    _make_song(lib, "s", stage="prompted", with_inputs=False)
    src = tmp_path / "take.mp3"
    src.write_bytes(b"audio")
    commands.cmd_import("s", src)
    assert src.exists()


def test_import_image_keeps_extension(lib, tmp_path):
    sdir = _make_song(lib, "s", stage="recorded", with_inputs=False)
    src = tmp_path / "Gemini_Generated_Image.png"
    src.write_bytes(b"img")
    assert commands.cmd_import("s", src) == sdir / "cover.png"


def test_import_moves_previous_file_to_raw(lib, tmp_path):
    sdir = _make_song(lib, "s", stage="prompted", with_inputs=False)
    (sdir / "track.mp3").write_bytes(b"old")
    src = tmp_path / "new.mp3"
    src.write_bytes(b"new")
    commands.cmd_import("s", src)
    assert (sdir / "track.mp3").read_bytes() == b"new"
    assert (sdir / "raw" / "track.mp3").read_bytes() == b"old"


def test_import_rejects_unknown_extension(lib, tmp_path):
    _make_song(lib, "s", stage="prompted", with_inputs=False)
    src = tmp_path / "notes.txt"
    src.write_text("x", encoding="utf-8")
    with pytest.raises(commands.CommandError) as err:
        commands.cmd_import("s", src)
    assert "unsupported file type" in str(err.value)


def test_import_missing_source(lib, tmp_path):
    _make_song(lib, "s", stage="prompted", with_inputs=False)
    with pytest.raises(commands.CommandError):
        commands.cmd_import("s", tmp_path / "nope.mp3")
```

- [ ] **Шаг 2: убедиться, что тесты падают**

Запустить: `.venv/bin/python -m pytest tests/test_commands.py -k import -v`
Ожидается: FAIL — `has no attribute 'cmd_import'`.

- [ ] **Шаг 3: реализовать**

Добавить `import shutil` и `from .inputs import AUDIO_EXTS, IMAGE_EXTS` в
`commands.py`:

```python
def cmd_import(slug: str, src) -> Path:
    sdir = _require_song(slug)
    source = Path(src)
    if not source.is_file():
        raise CommandError(f"File not found: {source}")
    ext = source.suffix.lower()
    if ext in AUDIO_EXTS:
        dest = sdir / "track.mp3"
    elif ext in IMAGE_EXTS:
        dest = sdir / f"cover{ext}"
    else:
        raise CommandError(f"unsupported file type: {ext or source.name}")
    _stash_existing(sdir, AUDIO_EXTS if ext in AUDIO_EXTS else IMAGE_EXTS)
    shutil.copy2(source, dest)
    return dest


def _stash_existing(song_dir: Path, exts: set) -> None:
    raw_dir = song_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    for entry in sorted(song_dir.iterdir()):
        if entry.is_file() and entry.suffix.lower() in exts:
            entry.rename(raw_dir / entry.name)
```

Копирование, а не перемещение: скачанный файл остаётся там, куда его положил
браузер, — пользователь не теряет исходник, если импорт был ошибочным.
Предыдущий файл того же типа уезжает в `raw/`, чтобы в корне всегда оставался
ровно один — инвариант, на который опирается `build`.

- [ ] **Шаг 4: прогнать тесты**

Запустить: `.venv/bin/python -m pytest tests/test_commands.py -v`
Ожидается: PASS.

- [ ] **Шаг 5: коммит**

```bash
git add sovigen/commands.py tests/test_commands.py
git commit -m "Add import command to place downloaded audio and covers"
```

---

### Задача 6: `status` с чьим ходом и `--json` в CLI

**Файлы:**
- Изменить: `sovigen/commands.py` (`cmd_status`), `sovigen/cli.py`
- Тест: `tests/test_commands.py`, `tests/test_cli.py`

**Интерфейсы:**
- Производит: `cmd_status() -> list[dict]` со значениями
  `{"slug", "title", "stage", "turn"}`, где `turn` ∈ `{"you", "claude", "-"}`;
  `TURN_BY_STAGE: dict[str, str]` в `commands.py`.

- [ ] **Шаг 1: написать падающие тесты**

В `tests/test_commands.py`:

```python
def test_status_reports_turn(lib):
    _make_song(lib, "a", stage="prompted", with_inputs=False)
    _make_song(lib, "b", stage="lyrics", with_inputs=False)
    _make_song(lib, "c", stage="published", with_inputs=False)
    rows = {row["slug"]: row["turn"] for row in commands.cmd_status()}
    assert rows == {"a": "you", "b": "claude", "c": "-"}
```

В `tests/test_cli.py`:

```python
def test_status_json_is_parseable(lib, capsys):
    commands.cmd_new("Мій щит")
    assert cli.main(["status", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["slug"] == "мій-щит"
    assert payload[0]["stage"] == "idea"


def test_advance_reports_transition(lib, capsys):
    sdir = commands.cmd_new("Мій щит")
    (sdir / "brief.md").write_text("x", encoding="utf-8")
    assert cli.main(["advance", "мій-щит"]) == 0
    assert "idea -> brief" in capsys.readouterr().out


def test_advance_missing_file_exits_nonzero(lib, capsys):
    sdir = commands.cmd_new("Мій щит")
    (sdir / "brief.md").unlink()
    assert cli.main(["advance", "мій-щит"]) == 1
    assert "missing: brief.md" in capsys.readouterr().err
```

В `tests/test_cli.py` добавить импорт `json`, `from sovigen import commands` и
фикстуру `lib`, если её там нет (скопировать из `tests/test_commands.py`).
Удалить существующие тесты про подкоманду `ready`.

- [ ] **Шаг 2: убедиться, что тесты падают**

Запустить: `.venv/bin/python -m pytest tests/test_cli.py -v`
Ожидается: FAIL — `unrecognized arguments: --json` и отсутствие `advance`.

- [ ] **Шаг 3: реализовать**

В `commands.py`:

```python
TURN_BY_STAGE = {
    "idea": "claude",
    "brief": "claude",
    "lyrics": "claude",
    "prompted": "you",
    "recorded": "claude",
    "ready": "claude",
    "pre-published": "you",
    "published": "-",
}


def cmd_status() -> list:
    rows = []
    for slug in paths.list_song_slugs():
        sdir = paths.song_dir(slug)
        row = {"slug": slug, "stage": "?", "title": slug, "turn": "-"}
        if meta_mod.has_meta(sdir):
            data = meta_mod.read_meta(sdir)
            row["stage"] = data.get("stage", "?")
            row["title"] = data.get("title", slug)
            row["turn"] = TURN_BY_STAGE.get(row["stage"], "-")
        rows.append(row)
    return rows
```

В `cli.py`: убрать парсер `ready`, добавить

```python
    p_advance = sub.add_parser("advance")
    p_advance.add_argument("slug")

    p_import = sub.add_parser("import")
    p_import.add_argument("slug")
    p_import.add_argument("path")

    p_new.add_argument("--source", default=None)
    p_new.add_argument("--series", default=None)
    p_new.add_argument("--language", default="uk")

    p_status = sub.add_parser("status")
    p_status.add_argument("--json", action="store_true")
```

и в `_dispatch`:

```python
    if args.command == "advance":
        moved_from, moved_to = commands.cmd_advance(args.slug)
        if moved_from == moved_to:
            print(f"{args.slug} already at {moved_to}")
        else:
            print(f"{args.slug}: {moved_from} -> {moved_to}")
        return 0
    if args.command == "import":
        dest = commands.cmd_import(args.slug, args.path)
        print(f"imported {dest}")
        return 0
    if args.command == "status":
        rows = commands.cmd_status()
        if args.json:
            print(json.dumps(rows, ensure_ascii=False))
        else:
            _print_status(rows)
        return 0
```

`cmd_new` вызывать с новыми аргументами; `_print_status` расширить колонкой
хода:

```python
def _print_status(rows) -> None:
    if not rows:
        print("no songs yet")
        return
    for row in rows:
        print(f"{row['stage']:<14} {row['turn']:<7} {row['slug']}")
```

Добавить `import json` в начало `cli.py`.

- [ ] **Шаг 4: прогнать весь сьют**

Запустить: `.venv/bin/python -m pytest -v`
Ожидается: PASS целиком.

- [ ] **Шаг 5: коммит**

```bash
git add sovigen/commands.py sovigen/cli.py tests/test_commands.py tests/test_cli.py
git commit -m "Expose advance, import and machine-readable status in the CLI"
```

---

### Задача 7: git, just, README

**Файлы:**
- Изменить: `.gitignore`, `justfile`, `README.md`
- Удалить: `РОЛЬ И ЦЕЛЬ.md` (переезжает в задаче 8), `prompts/`

- [ ] **Шаг 1: переписать `.gitignore`**

```gitignore
.venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/
.DS_Store

# Медиа песен: тяжёлое и невоспроизводимое из репозитория.
# Тексты, meta.json и md-артефакты — коммитятся.
library/**/*.mp3
library/**/*.wav
library/**/*.mp4
library/**/*.png
library/**/*.jpg
library/**/*.jpeg
library/**/*.webp
library/**/raw/

# AI-конфиги провайдеров
.claude/
```

- [ ] **Шаг 2: проверить, что в индекс попадает только текст**

Запустить: `git add -A --dry-run library/ | head -30`
Ожидается: в списке только `meta.json` и `*.md`; ни одного `.mp3`, `.mp4`,
`.png`.

- [ ] **Шаг 3: обновить `justfile`**

Заменить рецепт `ready` на:

```just
# advance a song to the next stage: just advance my-track-name
advance slug:
    {{python}} -m sovigen.cli advance "{{slug}}"

# place a downloaded file into the song folder: just import my-track ~/Downloads/take.mp3
import slug path:
    {{python}} -m sovigen.cli import "{{slug}}" "{{path}}"
```

- [ ] **Шаг 4: обновить `README.md`**

Переписать разделы «Как устроен пайплайн», «Рабочий процесс» и «Структура
кода» под восемь стадий, новые команды и папку `knowledge/`. Явно записать:
кто ходит на каждой стадии, что `library/` теперь частично в гите (тексты — да,
медиа — нет), и что вопрос сохранности медиа открыт (issue #1).

- [ ] **Шаг 5: прогнать сьют и закоммитить**

```bash
.venv/bin/python -m pytest
git add .gitignore justfile README.md library
git commit -m "Version song texts in git and document the eight-stage pipeline"
```

---

### Задача 8: база знаний — роль и ремесло

**Файлы:**
- Создать: `knowledge/README.md`, `knowledge/role.md`,
  `knowledge/craft/lyrics.md`, `knowledge/craft/suno.md`,
  `knowledge/craft/cover.md`, `knowledge/craft/youtube.md`
- Удалить: `РОЛЬ И ЦЕЛЬ.md`, `prompts/nano-banana-cover.md`

Тестов нет: это содержание, а не код.

- [ ] **Шаг 1: `knowledge/README.md` — карта базы**

Одна страница: что где лежит и в каком порядке это читать скиллу. Обязательно
перечислить `role.md`, `craft/`, `styles/`, `series/`, `log.md` с одной фразой
про каждый.

- [ ] **Шаг 2: `knowledge/role.md`**

Перенести из `РОЛЬ И ЦЕЛЬ.md` строки 1–12 и 75–79: два формата (иврит+Suno,
украинский переспів), правило «по умолчанию — украинский переспів»,
эстетическую склонность к камерному против пафоса, требование консистентного
формата между песнями. Убрать инструкции по настройке проекта в claude.ai
(строки 84–92) — они больше не про этот конвейер.

- [ ] **Шаг 3: `knowledge/craft/lyrics.md`**

Перенести из `РОЛЬ И ЦЕЛЬ.md` строки 13–34: сверка по public-domain источникам
(tehillim-online.com, Sefaria, mechon-mamre), запрет писать текст псалма по
памяти, запрет копировать защищённые переводы (Огиенко, Хоменко, Турконяк),
еврейская нумерация со сдвигом +1, честность про сжатия и перестановки, формат
выдачи и структурные теги.

- [ ] **Шаг 4: `knowledge/craft/suno.md`**

Перенести строки 45–61: два поля Style и Exclude Styles, полный рецепт против
завываний (позитивное описание вокала, список исключений, отказ от слов-триггеров
worship/spontaneous, `[Intro: instrumental only, no vocals]`, запрет филлеров),
одна языковая версия за раз, кириллица и транслитерация, подгонка BPM и размера,
приёмы против обрезания на трёх минутах.

- [ ] **Шаг 5: `knowledge/craft/cover.md`**

Перенести `prompts/nano-banana-cover.md` целиком, добавив ссылку `[[craft/youtube]]`.

- [ ] **Шаг 6: `knowledge/craft/youtube.md`**

Новый файл: шаблон заголовка ролика, структура описания, набор тегов. Опереться
на то, что уже стоит у опубликованных песен на канале.

- [ ] **Шаг 7: удалить исходники и закоммитить**

```bash
git rm "РОЛЬ И ЦЕЛЬ.md" prompts/nano-banana-cover.md
git add knowledge
git commit -m "Move the songwriting role and craft notes into the knowledge base"
```

---

### Задача 9: карточки стилей

**Файлы:**
- Создать: `knowledge/styles/hillsong.md`, `casting-crowns.md`,
  `king-and-country.md`, `elevation.md`, `cinematic-orchestral.md`,
  `intimate-folk.md`, `lauren-daigle.md`, `chris-tomlin.md`
- Создать: `knowledge/series/psalms.md`, `knowledge/log.md`

- [ ] **Шаг 1: написать первую карточку целиком как образец**

`knowledge/styles/casting-crowns.md`:

```markdown
---
style: casting-crowns
mood: покаяние, честный плач, «Бог в буре»
---

# Casting Crowns

Нарративный CCM поп-рок. Честный плач, а не декларация. Баритон, акустика в
начале, бэнд к середине, разрешение через доверие, а не через триумф.

## Style

```
contemporary Christian pop-rock ballad, male baritone lead, narrative delivery,
acoustic guitar intro building to full band, warm analog drums, clean
straight-tone vocal, syllabic delivery (one note per syllable), restrained
on-the-beat phrasing, no runs, no ad-libs
```

## Exclude Styles

```
melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh chants,
spontaneous worship, oversinging, vocal improvisation, EDM, trap drums
```

## Когда брать

Покаянные псалмы, псалмы жалобы с разрешением в доверие. Плохо ложится на
чистое славословие — там нужен анфем.

## Где применялся

<Пополняется скиллом `song-retro`: песня, сколько дублей, что получилось.>
```

- [ ] **Шаг 2: сделать остальные семь по этому же шаблону**

Источник содержания — `РОЛЬ И ЦЕЛЬ.md`, строки 63–73 (файл к этому моменту
удалён, взять из `git show HEAD~1:"РОЛЬ И ЦЕЛЬ.md"`):

- `hillsong` — анфемный worship, большой повторяемый хук, билд к анфему
- `king-and-country` — кинематографичная перкуссивная драма, для судных и эпик
- `elevation` — конгрегационный декларативный анфем, «arise»-энергия
- `cinematic-orchestral` — струнные, хор, эпик-билд, с пометкой «осторожно с пафосом»
- `intimate-folk` — Rich Mullins / Andrew Peterson / The Porter's Gate, тёплый
  человеческий масштаб, дульцимер и мандолина, без бомбаста
- `lauren-daigle` — соул-поп, тёплый, камерный
- `chris-tomlin` — певучий конгрегационный анфем про величие

В каждой карточке блок Exclude Styles начинается с того же антимелизменного
набора, что в образце: он общий для всех стилей и живёт в `craft/suno.md`, а в
карточке повторяется, чтобы строку можно было скопировать целиком.

- [ ] **Шаг 3: `knowledge/series/psalms.md`**

Таблица: номер псалма, слаг песни, стадия, стиль. Заполнить по уже сделанному
(`just status` плюс `meta.json` существующих песен) и оставить пустые строки
на ближайшие псалмы очереди.

- [ ] **Шаг 4: `knowledge/log.md`**

Пустой журнал с заголовком и одной фразой о формате записи: дата, песня, вывод.

- [ ] **Шаг 5: коммит**

```bash
git add knowledge
git commit -m "Add style presets, psalm series queue and the feedback log"
```

---

### Задача 10: скиллы творческих этапов

**Файлы:**
- Создать: `.claude/skills/song-brief/SKILL.md`,
  `.claude/skills/song-lyrics/SKILL.md`, `.claude/skills/song-suno/SKILL.md`

Не коммитятся: `.claude/` в `.gitignore`.

- [ ] **Шаг 1: `song-brief`**

Frontmatter `name`/`description` в стиле существующего `release-song`. Тело:
прочитать `knowledge/role.md` и `knowledge/craft/lyrics.md`; сверить текст
источника по public-domain источникам (не по памяти); заполнить `brief.md`
песни; предложить основной стиль и две альтернативы со ссылками на карточки;
показать концепцию пользователю тезисами и **остановиться** — это шлюз.
После «ок» записать выбранный стиль в `meta.json` (поле `style`) и вызвать
`just advance <slug>`.

- [ ] **Шаг 2: `song-lyrics`**

Прочитать `brief.md` песни и `knowledge/craft/lyrics.md`. Написать `lyrics.md`:
структурные теги, таблица «секция ↔ стих», раздел про отступления. Не
останавливаться — по спеке текст показывается вместе с `suno.md`. Вызвать
`just advance <slug>`.

- [ ] **Шаг 3: `song-suno`**

Прочитать `lyrics.md`, `knowledge/craft/suno.md` и карточку стиля из
`meta.json`. Заполнить `suno.md`. Вызвать `just advance <slug>`, затем
показать пользователю текст целиком и готовые строки Style/Exclude для
копирования — и остановиться: дальше человек идёт в Suno.

- [ ] **Шаг 4: проверить руками**

Прогнать `song-brief` на реальном псалме из очереди, убедиться, что
`brief.md` заполнен, стадия сдвинулась, а стиль записан в `meta.json`.

---

### Задача 11: скилл-оркестратор `song`

**Файлы:**
- Создать: `.claude/skills/song/SKILL.md`

- [ ] **Шаг 1: написать скилл**

Тело по шагам:

1. Определить песню: по имени от пользователя или по теме («песня по Псалму
   23») — слаг выводится тем же правилом, что в `slugify`. Если папки нет —
   `just new "<название>" --source psalm-23 --series psalms`.
2. Прочитать состояние: `python3 -m sovigen.cli status --json`, найти песню,
   взять `stage` и `turn`.
3. Завести todo на каждый оставшийся этап, чтобы путь был виден.
4. Идти по этапам, вызывая соответствующий скилл этапа. Остановка одна —
   после `brief`; `lyrics` и `suno` идут подряд и показываются вместе.
5. На стадии `prompted` сказать, что нужно сгенерить в Suno, и ждать. Когда
   пользователь называет выбранный дубль — найти файл (обычно свежий mp3 в
   `~/Downloads`), выполнить `just import <slug> <путь>` и `just advance`.
6. Никогда не двигать стадию без словесного «ок» на артефакт, который эта
   стадия закрывает.
7. В начале работы посмотреть `knowledge/series/psalms.md`: если готовых
   концепций меньше пяти, предложить пополнить запас — но только предложить.

- [ ] **Шаг 2: сквозная проверка**

Провести одну настоящую песню от `idea` до `prompted` через скилл `song`.
Убедиться: `meta.json` содержит `stage_history` со всеми переходами, все три
артефакта заполнены, ни один шлюз не проскочен без вопроса.

---

## Что остаётся за пределами фазы 1

Фаза 2 (`song-art`, `song-retro`, обновление `release-song`, `log.md`) и фаза 3
(`psalm-backlog`, команда `backlog`) — отдельные планы. Issue #1 (сохранность
медиа) — решение владельца, а не задача этого плана; `.gitignore` из задачи 7
даёт удалённую копию только текстам.
