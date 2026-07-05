# sovigen — конвейер релиза песен на YouTube

Инструмент собирает готовое видео для YouTube из **обложки** (картинка) и
**песни** (mp3): картинка вписывается в кадр 1920×1080, поверх ложится
аудио, на выходе — `youtube.mp4`.

Каждая песня — это постоянная папка `library/<slug>/`, а её состояние
хранится прямо рядом, в `meta.json` (поле `stage`). Никакой БД и внешних
сервисов: весь стейт — это файлы на диске. Поэтому конвейер переносится
между машинами простым копированием папки песни.

> В репозитории лежит **только код и описание пайплайна**. Сама библиотека
> песен (`library/`) — обложки, mp3, готовые видео — игнорируется гитом и
> живёт локально на каждой машине.

## Что нужно установить

| Зависимость | Зачем | Проверка |
|-------------|-------|----------|
| **Python 3.9+** | сам CLI (только стандартная библиотека, внешних пакетов нет) | `python3 --version` |
| **ffmpeg** (+ `ffprobe`) | сборка видео и проверка результата | `ffmpeg -version` |
| **just** *(опционально)* | удобные короткие команды из `justfile` | `just --version` |
| **pytest** *(только для тестов)* | прогон тест-сьюта, ставится в `.venv` | `just test` |

Установка системных зависимостей на macOS:

```bash
brew install ffmpeg just
```

CLI написан на чистой стандартной библиотеке Python, поэтому для генерации
песен `.venv` и pytest **не нужны** — достаточно `python3` и `ffmpeg` в PATH.
Виртуальное окружение требуется только чтобы прогонять тесты.

## Установка проекта на новой машине

```bash
git clone https://github.com/vladimirfriptu/sovigen.git
cd sovigen

# опционально — окружение для тестов
just setup          # создаёт .venv и ставит pytest
# или без just:
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
```

Папка `library/` создаётся автоматически при первой команде `new` — держать
её в репозитории не нужно.

## Как устроен пайплайн

Жизненный цикл песни описывается стадиями в `meta.json`:

```
draft ──► ready ──► pre-published ──► published
```

| Стадия | Что означает |
|--------|--------------|
| `draft` | папка создана, файлы ещё отбираются |
| `ready` | обложка и mp3 отобраны, можно собирать |
| `pre-published` | `youtube.mp4` собран, ждёт заливки на YouTube |
| `published` | видео залито на YouTube |

Внутри папки песни:

```
library/<slug>/
  meta.json                 # стейт: title, slug, stage, created
  cover.jpg | cover.png     # ровно одна обложка (.jpg/.jpeg/.png/.webp)
  track.mp3                 # ровно один аудиофайл (.mp3)
  raw/                      # свалка черновых вариантов — пайплайном игнорируется
  youtube.mp4               # результат сборки (после build)
```

Сборка (`build`) требует в корне папки **ровно один** аудиофайл и **ровно
одну** картинку; лишние варианты складывай в `raw/`, иначе пайплайн честно
откажется угадывать и попросит навести порядок.

## Рабочий процесс (через just)

```bash
just new "My Track Name"    # создаёт library/my-track-name (stage=draft)
                            # → положи обложку и track.mp3 в папку песни

just ready my-track-name    # stage → ready, когда файлы отобраны
just build my-track-name    # собирает youtube.mp4, stage → pre-published
just build-all              # собирает все песни со stage=ready

# залей youtube.mp4 на YouTube, затем:
just publish my-track-name  # stage → published

just status                 # таблица всех песен и их стадий
```

## Те же команды без just

`just` — это лишь тонкая обёртка над Python-модулем. Всё то же самое:

```bash
python3 -m sovigen.cli new "My Track Name"
python3 -m sovigen.cli ready my-track-name
python3 -m sovigen.cli build my-track-name
python3 -m sovigen.cli build-all
python3 -m sovigen.cli publish my-track-name
python3 -m sovigen.cli status
```

## Структура кода

```
sovigen/
  cli.py         # разбор аргументов и точка входа (argparse)
  commands.py    # логика команд new/build/build-all/ready/publish/status
  ffmpegcmd.py   # сборка ffmpeg-команды для статичного видео
  inputs.py      # поиск ровно одного аудио и одной картинки в папке
  meta.py        # чтение/запись meta.json и переходы по стадиям
  paths.py       # расположение library/ и папок песен
  slug.py        # slugify заголовка (Unicode-aware, сохраняет кириллицу)
prompts/
  nano-banana-cover.md   # базовый промпт для генерации обложки
tests/           # pytest-сьют на каждый модуль
```

## Формат видео

1920×1080, картинка вписана целиком с чёрным padding (ничего не
обрезается), `libx264` / `yuv420p`, аудио `aac 320k`, длительность = длине
песни, `+faststart` для быстрой отдачи. Точная команда — в
`sovigen/ffmpegcmd.py`.

## Обложки

Базовый промпт для генерации обложки (nano banana / Gemini image) лежит в
[`prompts/nano-banana-cover.md`](prompts/nano-banana-cover.md). Главное —
соблюсти 16:9 и безопасные отступы по краям; финальный кадр 1920×1080
всё равно соберёт `build`.

## Переменные окружения

| Переменная | По умолчанию | Назначение |
|------------|--------------|------------|
| `SOVIGEN_LIBRARY` | `library` | путь к каталогу с песнями (можно вынести на внешний диск) |

## Тесты

```bash
just test
# или
.venv/bin/python -m pytest
```

## На будущее (вне MVP)

Оживление обложки через Stable Video Diffusion + бесшовный луп/реверс —
команды `animate` и `build --render` зарезервированы, но не реализованы.
