# YouTube Release Pipeline — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Локальный CLI-пайплайн, который из обложки и mp3 собирает статичное видео под YouTube; песни хранятся как постоянные папки со стадией релиза в `meta.json`.

**Architecture:** Пакет `sovigen/` (чистый stdlib Python) с узкими модулями (slug, paths, meta, inputs, ffmpegcmd, commands, cli). `justfile` — тонкие обёртки над `python3 -m sovigen.cli`. Видео собирает `ffmpeg` через `subprocess`. Стадия песни — поле в `meta.json`, песня физически не перемещается.

**Tech Stack:** Python 3.13 (stdlib only в рантайме), ffmpeg 8, just 1.51, pytest (dev-only).

## Global Constraints

- Python: только stdlib в рантайме (`subprocess`, `json`, `pathlib`, `argparse`, `re`, `datetime`, `os`). Никаких torch / moviepy / diffusers в MVP.
- Пакет лежит в корне репо: `sovigen/`. Запуск: `python3 -m sovigen.cli <cmd>`.
- Путь к библиотеке: env `SOVIGEN_LIBRARY`, по умолчанию `library` (относительно cwd).
- Стадии песни ровно: `draft`, `ready`, `pre-published`, `published` (именно эти строки).
- Выходной файл: `youtube.mp4` в корне папки песни. Не перезаписываем молча.
- Целевой формат: холст 1920×1080, картинку вписываем целиком + чёрный pad, `libx264` / `-tune stillimage` / `yuv420p`, аудио `aac 320k`, длина = аудио.
- Картинки в подпапке `raw/` игнорируются (это свалка); входные файлы ищем только в корне папки песни.
- Все команды кроме `build-all` и `status` принимают **slug** песни.
- Артефакты `.claude/` и `library/` не коммитим.

---

### Task 1: Scaffolding + slugify

**Files:**
- Create: `sovigen/__init__.py`
- Create: `sovigen/slug.py`
- Create: `tests/__init__.py`
- Create: `tests/test_slug.py`
- Create: `pyproject.toml`
- Create: `requirements-dev.txt`
- Create: `.gitignore`

**Interfaces:**
- Consumes: nothing.
- Produces: `slugify(title: str) -> str` — нижний регистр, неалфанумерики (с поддержкой Unicode/кириллицы) → дефисы, обрезка крайних дефисов. Пустой результат возможен (вызывающий проверяет сам).

- [ ] **Step 1: Create project config files**

`pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

`requirements-dev.txt`:
```
pytest
```

`.gitignore`:
```
.venv/
__pycache__/
*.pyc
*.pyo
library/
.claude/
```

`sovigen/__init__.py`:
```python
```
(пустой файл)

`tests/__init__.py`:
```python
```
(пустой файл)

- [ ] **Step 2: Write the failing test**

`tests/test_slug.py`:
```python
from sovigen.slug import slugify


def test_basic_spaces_and_case():
    assert slugify("My Track Name") == "my-track-name"


def test_trims_and_collapses_punctuation():
    assert slugify("  Hello,   World!!  ") == "hello-world"


def test_keeps_cyrillic():
    assert slugify("Привет Мир") == "привет-мир"


def test_underscores_become_hyphens():
    assert slugify("a_b__c") == "a-b-c"


def test_symbols_only_yields_empty():
    assert slugify("!!! ???") == ""
```

- [ ] **Step 3: Run test to verify it fails**

Run: `python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt && .venv/bin/python -m pytest tests/test_slug.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'sovigen.slug'`

- [ ] **Step 4: Write minimal implementation**

`sovigen/slug.py`:
```python
import re


def slugify(title: str) -> str:
    lowered = title.strip().lower()
    cleaned = re.sub(r"[^\w]+", "-", lowered, flags=re.UNICODE)
    collapsed = re.sub(r"_+", "-", cleaned)
    trimmed = collapsed.strip("-")
    return trimmed
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_slug.py`
Expected: PASS (5 passed)

- [ ] **Step 6: Commit**

```bash
git init
git add pyproject.toml requirements-dev.txt .gitignore sovigen/__init__.py sovigen/slug.py tests/__init__.py tests/test_slug.py
git commit -m "feat: project scaffolding and slugify"
```

---

### Task 2: Library paths

**Files:**
- Create: `sovigen/paths.py`
- Create: `tests/test_paths.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `library_dir() -> Path` — `Path(os.environ["SOVIGEN_LIBRARY"])` если задан, иначе `Path("library")`.
  - `song_dir(slug: str) -> Path` — `library_dir() / slug`.
  - `list_song_slugs() -> list[str]` — отсортированные имена подпапок в `library_dir()`; `[]` если библиотеки нет.

- [ ] **Step 1: Write the failing test**

`tests/test_paths.py`:
```python
from pathlib import Path

from sovigen import paths


def test_library_dir_from_env(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path / "lib"))
    assert paths.library_dir() == tmp_path / "lib"


def test_library_dir_default(monkeypatch):
    monkeypatch.delenv("SOVIGEN_LIBRARY", raising=False)
    assert paths.library_dir() == Path("library")


def test_song_dir(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    assert paths.song_dir("foo") == tmp_path / "foo"


def test_list_song_slugs_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path / "missing"))
    assert paths.list_song_slugs() == []


def test_list_song_slugs_sorted(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path))
    (tmp_path / "b-song").mkdir()
    (tmp_path / "a-song").mkdir()
    (tmp_path / "note.txt").write_text("x")
    assert paths.list_song_slugs() == ["a-song", "b-song"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_paths.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'sovigen.paths'`

- [ ] **Step 3: Write minimal implementation**

`sovigen/paths.py`:
```python
import os
from pathlib import Path


def library_dir() -> Path:
    override = os.environ.get("SOVIGEN_LIBRARY")
    if override:
        return Path(override)
    return Path("library")


def song_dir(slug: str) -> Path:
    base = library_dir()
    return base / slug


def list_song_slugs() -> list[str]:
    base = library_dir()
    if not base.exists():
        return []
    slugs = []
    for entry in sorted(base.iterdir()):
        if entry.is_dir():
            slugs.append(entry.name)
    return slugs
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_paths.py`
Expected: PASS (5 passed)

- [ ] **Step 5: Commit**

```bash
git add sovigen/paths.py tests/test_paths.py
git commit -m "feat: library path resolution"
```

---

### Task 3: meta.json read/write/stage

**Files:**
- Create: `sovigen/meta.py`
- Create: `tests/test_meta.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `STAGES: list[str]` = `["draft", "ready", "pre-published", "published"]`.
  - `new_meta(title: str, slug: str, created: str) -> dict` → `{"title","slug","stage":"draft","created"}`.
  - `meta_path(song_dir: Path) -> Path` → `song_dir / "meta.json"`.
  - `has_meta(song_dir: Path) -> bool`.
  - `read_meta(song_dir: Path) -> dict`.
  - `write_meta(song_dir: Path, meta: dict) -> None` (UTF-8, `ensure_ascii=False`, отступ 2, перевод строки в конце).
  - `set_stage(song_dir: Path, stage: str) -> None` — `ValueError` если стадия не из `STAGES`.

- [ ] **Step 1: Write the failing test**

`tests/test_meta.py`:
```python
import pytest

from sovigen import meta


def test_new_meta_shape():
    data = meta.new_meta("My Song", "my-song", "2026-06-22")
    assert data == {
        "title": "My Song",
        "slug": "my-song",
        "stage": "draft",
        "created": "2026-06-22",
    }


def test_write_then_read_roundtrip(tmp_path):
    data = meta.new_meta("Привет", "privet", "2026-06-22")
    meta.write_meta(tmp_path, data)
    assert meta.read_meta(tmp_path) == data


def test_write_preserves_cyrillic_unescaped(tmp_path):
    meta.write_meta(tmp_path, meta.new_meta("Привет", "privet", "2026-06-22"))
    text = (tmp_path / "meta.json").read_text(encoding="utf-8")
    assert "Привет" in text


def test_has_meta(tmp_path):
    assert meta.has_meta(tmp_path) is False
    meta.write_meta(tmp_path, meta.new_meta("X", "x", "2026-06-22"))
    assert meta.has_meta(tmp_path) is True


def test_set_stage_valid(tmp_path):
    meta.write_meta(tmp_path, meta.new_meta("X", "x", "2026-06-22"))
    meta.set_stage(tmp_path, "ready")
    assert meta.read_meta(tmp_path)["stage"] == "ready"


def test_set_stage_invalid(tmp_path):
    meta.write_meta(tmp_path, meta.new_meta("X", "x", "2026-06-22"))
    with pytest.raises(ValueError):
        meta.set_stage(tmp_path, "bogus")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_meta.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'sovigen.meta'`

- [ ] **Step 3: Write minimal implementation**

`sovigen/meta.py`:
```python
import json
from pathlib import Path

STAGES = ["draft", "ready", "pre-published", "published"]
META_FILENAME = "meta.json"


def new_meta(title: str, slug: str, created: str) -> dict:
    return {"title": title, "slug": slug, "stage": "draft", "created": created}


def meta_path(song_dir: Path) -> Path:
    return song_dir / META_FILENAME


def has_meta(song_dir: Path) -> bool:
    return meta_path(song_dir).exists()


def read_meta(song_dir: Path) -> dict:
    path = meta_path(song_dir)
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def write_meta(song_dir: Path, meta: dict) -> None:
    path = meta_path(song_dir)
    text = json.dumps(meta, ensure_ascii=False, indent=2)
    path.write_text(text + "\n", encoding="utf-8")


def set_stage(song_dir: Path, stage: str) -> None:
    if stage not in STAGES:
        raise ValueError(f"Unknown stage: {stage}")
    data = read_meta(song_dir)
    data["stage"] = stage
    write_meta(song_dir, data)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_meta.py`
Expected: PASS (6 passed)

- [ ] **Step 5: Commit**

```bash
git add sovigen/meta.py tests/test_meta.py
git commit -m "feat: meta.json read/write and stage transitions"
```

---

### Task 4: Input file discovery

**Files:**
- Create: `sovigen/inputs.py`
- Create: `tests/test_inputs.py`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `InputError(Exception)`.
  - `find_audio(song_dir: Path) -> Path` — единственный `*.mp3` в корне папки; `InputError` если 0 или >1.
  - `find_image(song_dir: Path) -> Path` — единственный `*.jpg/.jpeg/.png/.webp` в корне папки; `InputError` если 0 или >1.
  - Файлы в подпапках (например `raw/`) игнорируются: ищем только файлы корня (`is_file()`).

- [ ] **Step 1: Write the failing test**

`tests/test_inputs.py`:
```python
import pytest

from sovigen.inputs import InputError, find_audio, find_image


def _touch(p):
    p.write_bytes(b"")


def test_find_audio_single(tmp_path):
    _touch(tmp_path / "track.mp3")
    assert find_audio(tmp_path) == tmp_path / "track.mp3"


def test_find_audio_none(tmp_path):
    with pytest.raises(InputError):
        find_audio(tmp_path)


def test_find_audio_multiple(tmp_path):
    _touch(tmp_path / "a.mp3")
    _touch(tmp_path / "b.mp3")
    with pytest.raises(InputError):
        find_audio(tmp_path)


def test_find_image_single_case_insensitive(tmp_path):
    _touch(tmp_path / "cover.JPG")
    assert find_image(tmp_path) == tmp_path / "cover.JPG"


def test_find_image_ignores_raw_subdir(tmp_path):
    (tmp_path / "raw").mkdir()
    _touch(tmp_path / "raw" / "a.png")
    _touch(tmp_path / "raw" / "b.png")
    _touch(tmp_path / "cover.png")
    assert find_image(tmp_path) == tmp_path / "cover.png"


def test_find_image_multiple_in_root(tmp_path):
    _touch(tmp_path / "a.png")
    _touch(tmp_path / "b.jpg")
    with pytest.raises(InputError):
        find_image(tmp_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_inputs.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'sovigen.inputs'`

- [ ] **Step 3: Write minimal implementation**

`sovigen/inputs.py`:
```python
from pathlib import Path

AUDIO_EXTS = {".mp3"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


class InputError(Exception):
    pass


def _find_single(song_dir: Path, exts: set, kind: str) -> Path:
    matches = []
    for entry in sorted(song_dir.iterdir()):
        if entry.is_file() and entry.suffix.lower() in exts:
            matches.append(entry)
    if len(matches) == 0:
        raise InputError(f"No {kind} found in {song_dir}")
    if len(matches) > 1:
        names = ", ".join(m.name for m in matches)
        raise InputError(f"Multiple {kind} files in {song_dir}: {names}")
    return matches[0]


def find_audio(song_dir: Path) -> Path:
    return _find_single(song_dir, AUDIO_EXTS, "audio (.mp3)")


def find_image(song_dir: Path) -> Path:
    return _find_single(song_dir, IMAGE_EXTS, "image")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_inputs.py`
Expected: PASS (6 passed)

- [ ] **Step 5: Commit**

```bash
git add sovigen/inputs.py tests/test_inputs.py
git commit -m "feat: input mp3/image discovery"
```

---

### Task 5: ffmpeg command builder

**Files:**
- Create: `sovigen/ffmpegcmd.py`
- Create: `tests/test_ffmpegcmd.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `build_static_video_cmd(image: Path, audio: Path, output: Path) -> list[str]` — список аргументов для `subprocess.run` (первый элемент `"ffmpeg"`).

- [ ] **Step 1: Write the failing test**

`tests/test_ffmpegcmd.py`:
```python
from pathlib import Path

from sovigen.ffmpegcmd import build_static_video_cmd


def test_cmd_starts_with_ffmpeg_and_inputs():
    cmd = build_static_video_cmd(Path("c.jpg"), Path("t.mp3"), Path("out.mp4"))
    assert cmd[0] == "ffmpeg"
    assert "c.jpg" in cmd
    assert "t.mp3" in cmd
    assert cmd[-1] == "out.mp4"


def test_cmd_has_youtube_encoding_flags():
    cmd = build_static_video_cmd(Path("c.jpg"), Path("t.mp3"), Path("out.mp4"))
    joined = " ".join(cmd)
    assert "libx264" in cmd
    assert "stillimage" in cmd
    assert "aac" in cmd
    assert "320k" in cmd
    assert "-shortest" in cmd
    assert "1920:1080" in joined
    assert "yuv420p" in joined
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_ffmpegcmd.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'sovigen.ffmpegcmd'`

- [ ] **Step 3: Write minimal implementation**

`sovigen/ffmpegcmd.py`:
```python
from pathlib import Path

VIDEO_FILTER = (
    "scale=1920:1080:force_original_aspect_ratio=decrease,"
    "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,"
    "format=yuv420p"
)


def build_static_video_cmd(image: Path, audio: Path, output: Path) -> list:
    return [
        "ffmpeg",
        "-loop", "1",
        "-framerate", "2",
        "-i", str(image),
        "-i", str(audio),
        "-vf", VIDEO_FILTER,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-r", "24",
        "-c:a", "aac",
        "-b:a", "320k",
        "-shortest",
        "-movflags", "+faststart",
        "-y",
        str(output),
    ]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_ffmpegcmd.py`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add sovigen/ffmpegcmd.py tests/test_ffmpegcmd.py
git commit -m "feat: ffmpeg static-video command builder"
```

---

### Task 6: Commands orchestration

**Files:**
- Create: `sovigen/commands.py`
- Create: `tests/test_commands.py`

**Interfaces:**
- Consumes: `slug.slugify`, `paths.*`, `meta.*`, `inputs.find_audio/find_image`, `ffmpegcmd.build_static_video_cmd`.
- Produces:
  - `CommandError(Exception)`.
  - `cmd_new(title: str) -> Path` — создаёт `library/<slug>/raw/` и `meta.json` (stage `draft`); `CommandError` если slug пустой или папка существует.
  - `cmd_build(slug: str) -> Path` — проверяет существование песни и отсутствие `youtube.mp4`, находит входы, запускает ffmpeg через `subprocess.run`, при успехе ставит stage `pre-published`, возвращает путь к `youtube.mp4`.
  - `cmd_build_all() -> list[str]` — собирает все песни со stage `ready` (папки без `meta.json` пропускает); возвращает список собранных slug.
  - `cmd_publish(slug: str) -> None` — ставит stage `published`.
  - `cmd_status() -> list[dict]` — `[{"slug","stage","title"}]` по всем песням (без `meta.json` → stage `"?"`).

- [ ] **Step 1: Write the failing test**

`tests/test_commands.py`:
```python
import subprocess

import pytest

from sovigen import commands, meta


@pytest.fixture
def lib(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path / "library"))
    return tmp_path / "library"


def _make_song(lib, slug, stage="draft", with_inputs=True):
    sdir = lib / slug
    (sdir / "raw").mkdir(parents=True)
    meta.write_meta(sdir, meta.new_meta(slug, slug, "2026-06-22"))
    if stage != "draft":
        meta.set_stage(sdir, stage)
    if with_inputs:
        (sdir / "cover.png").write_bytes(b"")
        (sdir / "track.mp3").write_bytes(b"")
    return sdir


def _fake_ffmpeg_ok(monkeypatch):
    def fake_run(cmd, capture_output=True, text=True):
        output = cmd[-1]
        open(output, "wb").close()

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)


def test_new_creates_structure(lib):
    sdir = commands.cmd_new("My Track Name")
    assert sdir == lib / "my-track-name"
    assert (sdir / "raw").is_dir()
    assert meta.read_meta(sdir)["stage"] == "draft"
    assert meta.read_meta(sdir)["title"] == "My Track Name"


def test_new_rejects_existing(lib):
    commands.cmd_new("Dup")
    with pytest.raises(commands.CommandError):
        commands.cmd_new("Dup")


def test_new_rejects_empty_slug(lib):
    with pytest.raises(commands.CommandError):
        commands.cmd_new("!!!")


def test_build_happy_path(lib, monkeypatch):
    _make_song(lib, "song-a", stage="ready")
    _fake_ffmpeg_ok(monkeypatch)
    out = commands.cmd_build("song-a")
    assert out.exists()
    assert out.name == "youtube.mp4"
    assert meta.read_meta(lib / "song-a")["stage"] == "pre-published"


def test_build_unknown_slug(lib):
    with pytest.raises(commands.CommandError):
        commands.cmd_build("nope")


def test_build_refuses_existing_output(lib, monkeypatch):
    sdir = _make_song(lib, "song-b", stage="ready")
    (sdir / "youtube.mp4").write_bytes(b"")
    _fake_ffmpeg_ok(monkeypatch)
    with pytest.raises(commands.CommandError):
        commands.cmd_build("song-b")


def test_build_ffmpeg_failure_keeps_stage(lib, monkeypatch):
    _make_song(lib, "song-c", stage="ready")

    def fake_run(cmd, capture_output=True, text=True):
        class R:
            returncode = 1
            stderr = "boom"

        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(commands.CommandError):
        commands.cmd_build("song-c")
    assert meta.read_meta(lib / "song-c")["stage"] == "ready"


def test_build_all_only_ready(lib, monkeypatch):
    _make_song(lib, "ready-one", stage="ready")
    _make_song(lib, "draft-one", stage="draft")
    _fake_ffmpeg_ok(monkeypatch)
    built = commands.cmd_build_all()
    assert built == ["ready-one"]
    assert meta.read_meta(lib / "ready-one")["stage"] == "pre-published"
    assert meta.read_meta(lib / "draft-one")["stage"] == "draft"


def test_build_all_skips_dirs_without_meta(lib, monkeypatch):
    (lib / "junk").mkdir(parents=True)
    _fake_ffmpeg_ok(monkeypatch)
    assert commands.cmd_build_all() == []


def test_publish_sets_stage(lib):
    _make_song(lib, "song-d", stage="pre-published")
    commands.cmd_publish("song-d")
    assert meta.read_meta(lib / "song-d")["stage"] == "published"


def test_status_lists_rows(lib):
    _make_song(lib, "song-e", stage="ready")
    rows = commands.cmd_status()
    assert {"slug": "song-e", "stage": "ready", "title": "song-e"} in rows
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_commands.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'sovigen.commands'`

- [ ] **Step 3: Write minimal implementation**

`sovigen/commands.py`:
```python
import datetime
import subprocess
from pathlib import Path

from . import meta as meta_mod
from . import paths
from .ffmpegcmd import build_static_video_cmd
from .inputs import find_audio, find_image
from .slug import slugify

OUTPUT_FILENAME = "youtube.mp4"


class CommandError(Exception):
    pass


def _require_song(slug: str) -> Path:
    sdir = paths.song_dir(slug)
    if not sdir.is_dir():
        available = ", ".join(paths.list_song_slugs()) or "(none)"
        raise CommandError(f"Song not found: {slug}. Available: {available}")
    return sdir


def cmd_new(title: str) -> Path:
    slug = slugify(title)
    if not slug:
        raise CommandError(f"Could not derive a slug from title: {title!r}")
    sdir = paths.song_dir(slug)
    if sdir.exists():
        raise CommandError(f"Song already exists: {slug}")
    raw_dir = sdir / "raw"
    raw_dir.mkdir(parents=True)
    today = datetime.date.today().isoformat()
    data = meta_mod.new_meta(title, slug, today)
    meta_mod.write_meta(sdir, data)
    return sdir


def cmd_build(slug: str) -> Path:
    sdir = _require_song(slug)
    output = sdir / OUTPUT_FILENAME
    if output.exists():
        raise CommandError(f"{OUTPUT_FILENAME} already exists for {slug}")
    image = find_image(sdir)
    audio = find_audio(sdir)
    cmd = build_static_video_cmd(image, audio, output)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise CommandError(f"ffmpeg failed for {slug}:\n{result.stderr}")
    meta_mod.set_stage(sdir, "pre-published")
    return output


def cmd_build_all() -> list:
    built = []
    for slug in paths.list_song_slugs():
        sdir = paths.song_dir(slug)
        if not meta_mod.has_meta(sdir):
            continue
        data = meta_mod.read_meta(sdir)
        if data.get("stage") == "ready":
            cmd_build(slug)
            built.append(slug)
    return built


def cmd_publish(slug: str) -> None:
    sdir = _require_song(slug)
    meta_mod.set_stage(sdir, "published")


def cmd_status() -> list:
    rows = []
    for slug in paths.list_song_slugs():
        sdir = paths.song_dir(slug)
        row = {"slug": slug, "stage": "?", "title": slug}
        if meta_mod.has_meta(sdir):
            data = meta_mod.read_meta(sdir)
            row["stage"] = data.get("stage", "?")
            row["title"] = data.get("title", slug)
        rows.append(row)
    return rows
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_commands.py`
Expected: PASS (11 passed)

- [ ] **Step 5: Commit**

```bash
git add sovigen/commands.py tests/test_commands.py
git commit -m "feat: new/build/build-all/publish/status commands"
```

---

### Task 7: CLI + justfile

**Files:**
- Create: `sovigen/cli.py`
- Create: `tests/test_cli.py`
- Create: `justfile`

**Interfaces:**
- Consumes: `commands.*`.
- Produces: `main(argv=None) -> int` — argparse-диспетчер подкоманд `new|build|build-all|publish|status`; печатает результат, ловит `CommandError` → stderr + код 1.

- [ ] **Step 1: Write the failing test**

`tests/test_cli.py`:
```python
import subprocess

import pytest

from sovigen import meta
from sovigen.cli import main


@pytest.fixture
def lib(monkeypatch, tmp_path):
    monkeypatch.setenv("SOVIGEN_LIBRARY", str(tmp_path / "library"))
    return tmp_path / "library"


def test_new_then_status(lib, capsys):
    assert main(["new", "Hello World"]) == 0
    assert (lib / "hello-world" / "meta.json").exists()
    assert main(["status"]) == 0
    out = capsys.readouterr().out
    assert "hello-world" in out
    assert "draft" in out


def test_unknown_slug_returns_1(lib, capsys):
    rc = main(["build", "ghost"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "Song not found" in err


def test_full_flow(lib, monkeypatch, capsys):
    main(["new", "Flow Song"])
    sdir = lib / "flow-song"
    (sdir / "cover.png").write_bytes(b"")
    (sdir / "track.mp3").write_bytes(b"")
    meta.set_stage(sdir, "ready")

    def fake_run(cmd, capture_output=True, text=True):
        open(cmd[-1], "wb").close()

        class R:
            returncode = 0
            stderr = ""

        return R()

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert main(["build-all"]) == 0
    assert (sdir / "youtube.mp4").exists()
    assert meta.read_meta(sdir)["stage"] == "pre-published"
    assert main(["publish", "flow-song"]) == 0
    assert meta.read_meta(sdir)["stage"] == "published"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_cli.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'sovigen.cli'`

- [ ] **Step 3: Write minimal implementation**

`sovigen/cli.py`:
```python
import argparse
import sys

from . import commands


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="sovigen")
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new")
    p_new.add_argument("title")

    p_build = sub.add_parser("build")
    p_build.add_argument("slug")

    sub.add_parser("build-all")

    p_pub = sub.add_parser("publish")
    p_pub.add_argument("slug")

    sub.add_parser("status")

    args = parser.parse_args(argv)
    try:
        return _dispatch(args)
    except commands.CommandError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1


def _dispatch(args) -> int:
    if args.command == "new":
        sdir = commands.cmd_new(args.title)
        print(f"created {sdir}")
        print("put cover.(jpg|png|webp) and track.mp3 inside, then set stage to 'ready'")
        return 0
    if args.command == "build":
        out = commands.cmd_build(args.slug)
        print(f"built {out}")
        return 0
    if args.command == "build-all":
        built = commands.cmd_build_all()
        if built:
            print("built: " + ", ".join(built))
        else:
            print("nothing to build (no songs at stage 'ready')")
        return 0
    if args.command == "publish":
        commands.cmd_publish(args.slug)
        print(f"published {args.slug}")
        return 0
    if args.command == "status":
        rows = commands.cmd_status()
        _print_status(rows)
        return 0
    return 2


def _print_status(rows) -> None:
    if not rows:
        print("no songs yet")
        return
    for row in rows:
        print(f"{row['stage']:<14} {row['slug']}")


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_cli.py`
Expected: PASS (3 passed)

- [ ] **Step 5: Create justfile**

`justfile`:
```just
python := "python3"

# install dev deps into .venv
setup:
    {{python}} -m venv .venv
    .venv/bin/pip install -r requirements-dev.txt

# run the test suite
test:
    .venv/bin/python -m pytest

# create a new song folder: just new "My Track Name"
new title:
    {{python}} -m sovigen.cli new "{{title}}"

# build one song by slug: just build my-track-name
build slug:
    {{python}} -m sovigen.cli build "{{slug}}"

# build every song at stage 'ready'
build-all:
    {{python}} -m sovigen.cli build-all

# mark a song published: just publish my-track-name
publish slug:
    {{python}} -m sovigen.cli publish "{{slug}}"

# show all songs and their stages
status:
    {{python}} -m sovigen.cli status
```

- [ ] **Step 6: Verify full suite + justfile wiring**

Run: `.venv/bin/python -m pytest && just status`
Expected: all tests PASS; `just status` prints `no songs yet` (or existing songs).

- [ ] **Step 7: Commit**

```bash
git add sovigen/cli.py tests/test_cli.py justfile
git commit -m "feat: argparse CLI and justfile recipes"
```

---

### Task 8: nano-banana prompt + README

**Files:**
- Create: `prompts/nano-banana-cover.md`
- Create: `README.md`

**Interfaces:**
- Consumes: nothing (documentation artifacts).
- Produces: nothing imported by code.

- [ ] **Step 1: Create the nano-banana prompt template**

`prompts/nano-banana-cover.md`:
```markdown
# Базовый промпт для обложки песни (nano banana / Gemini image)

Заполни плейсхолдеры в `{ }` и вставь промпт целиком.

## Промпт

Generate a music cover artwork in **16:9 widescreen aspect ratio,
1920×1080 pixels**.

Mood / theme: {настроение и тема песни — например "meditative ambient,
foggy pine forest at dawn, cold blue palette"}.
Visual style: {стиль — например "cinematic photographic", "hand-painted
illustration", "retro film grain"}.

Composition requirements:
- Keep the main subject centered.
- Leave generous safe margins: no important element within the outer ~8%
  of any edge (so the frame survives padding/cropping for video).
- No text, no watermarks, no logos, no borders.
- Even, balanced lighting; avoid extreme detail in the far corners.

Output a single full-bleed image at 16:9, 1920×1080.

## Заметки

- Если nano banana не держит точный размер — главное соблюсти 16:9 и
  безопасные отступы; пайплайн (`just build`) всё равно впишет картинку в
  1920×1080 с чёрным padding, ничего не обрезая.
- Сгенерированную картинку положи в папку песни как `cover.jpg`/`.png`.
```

- [ ] **Step 2: Create README**

`README.md`:
```markdown
# sovigen — YouTube release pipeline

Собирает видео для YouTube из обложки и mp3. Каждая песня — постоянная
папка в `library/<slug>/` со стадией релиза в `meta.json`.

## Установка

```bash
just setup        # создаёт .venv и ставит pytest
```

Требуется `ffmpeg` в PATH.

## Жизненный цикл песни

Стадии: `draft → ready → pre-published → published` (поле `stage` в `meta.json`).

```bash
just new "My Track Name"     # создаёт library/my-track-name (stage=draft)
# положи cover.(jpg|png|webp) и track.mp3 в папку песни;
# свалку вариантов держи в library/my-track-name/raw/
# когда готов — выставь "stage": "ready" в meta.json
just build my-track-name     # собирает youtube.mp4, stage -> pre-published
just build-all               # собирает все песни со stage=ready
# загрузи youtube.mp4 на YouTube, затем:
just publish my-track-name   # stage -> published
just status                  # таблица всех песен и их стадий
```

## Формат видео

1920×1080, картинка вписана целиком с чёрным padding, libx264/yuv420p,
аудио aac 320k, длительность = длине песни.

## Обложки

Базовый промпт для генерации обложки — `prompts/nano-banana-cover.md`.

## Тесты

```bash
just test
```

## На будущее (вне MVP)

Оживление обложки через Stable Video Diffusion + бесшовный луп/реверс —
команды `animate` и `build --render` зарезервированы, но не реализованы.
```

- [ ] **Step 3: Commit**

```bash
git add prompts/nano-banana-cover.md README.md
git commit -m "docs: nano-banana cover prompt and README"
```

---

## Self-Review

**Spec coverage:**
- Per-song folder + `meta.json` stage → Tasks 2, 3, 6. ✓
- `raw/` свалка игнорируется → Task 4 (`is_file()`), Task 6 (`new` создаёт `raw/`). ✓
- Команды `new/build/build-all/publish/status` + slug-аргумент → Tasks 6, 7. ✓
- Правило «1 mp3 + 1 картинка, иначе ошибка» → Task 4. ✓
- Идемпотентность (только `ready` → `pre-published`) → Task 6 `cmd_build_all`. ✓
- Не перезаписывать `youtube.mp4` → Task 6 `cmd_build`. ✓
- ffmpeg формат (1920×1080/pad/libx264/yuv420p/aac 320k/shortest) → Task 5. ✓
- nano-banana промпт-файл → Task 8. ✓
- Обработка ошибок (slug не найден, ffmpeg fail не меняет стадию) → Tasks 6, 7. ✓
- Будущее (animate) — задокументировано, не реализуется. ✓

**Placeholder scan:** нет TBD/TODO; весь код приведён полностью.

**Type consistency:** `slugify`, `library_dir/song_dir/list_song_slugs`, `new_meta/read_meta/write_meta/set_stage/has_meta`, `find_audio/find_image`, `build_static_video_cmd`, `cmd_*`, `main` — имена и сигнатуры совпадают между задачами и тестами.
```

