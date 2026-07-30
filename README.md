# sovigen — конвейер релиза песен на YouTube

Инструмент ведёт песню через восемь стадий — от идеи до публикации — и
на последнем шаге собирает готовое видео для YouTube из **обложки**
(картинка) и **песни** (mp3): картинка вписывается в кадр 1920×1080,
поверх ложится аудио, на выходе — `youtube.mp4`.

Каждая песня — это постоянная папка `library/<slug>/`, а её состояние
хранится прямо рядом, в `meta.json` (поле `stage`). Никакой БД и внешних
сервисов: весь стейт — это файлы на диске.

> **Что коммитится, а что нет.** Текст песни — `meta.json`, `brief.md`,
> `lyrics.md`, `suno.md`, `cover-prompt.md`, `youtube.md`, `notes.md` —
> версионируется в гите: у него есть история, и он приезжает на любую
> машину простым `git pull`. Медиа — `track.mp3`, `cover.*`,
> `youtube.mp4` — и черновая свалка `raw/` в гит не попадают
> (см. `.gitignore`): они тяжёлые и раздули бы публичный репозиторий.
> Долговременное хранение медиа — открытый вопрос, решения пока нет,
> отслеживается в issue [#1](https://github.com/vladimirfriptu/sovigen/issues/1).

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

`git clone` уже принесёт `library/` с текстами всех существующих песен
(без медиа) — докачивать mp3/обложки/видео для уже опубликованных треков
не нужно, они появляются заново только для новой песни.

## Как устроен пайплайн

Жизненный цикл песни — восемь стадий в `meta.json`:

```
idea → brief → lyrics → prompted → recorded → ready → pre-published → published
```

| Стадия | Что означает | Чей ход |
|--------|--------------|---------|
| `idea` | папка создана, тема ещё не сформулирована | Claude |
| `brief` | `brief.md` написан — о чём песня | Claude |
| `lyrics` | `lyrics.md` готов — финальный текст | Claude |
| `prompted` | `suno.md` готов — промпт для Suno | вы (сгенерировать в Suno) |
| `recorded` | трек скачан и лежит в папке как `track.mp3` | Claude |
| `ready` | обложка и `youtube.md` готовы, можно собирать видео | Claude |
| `pre-published` | `youtube.mp4` собран | вы (залить на YouTube) |
| `published` | видео опубликовано | — |

Переход между стадиями делает команда `advance`: она проверяет, что для
следующей стадии есть все нужные файлы, и только тогда двигает `stage`
вперёд. Стадии `prompted` и `pre-published` — это стадии, где ход за
человеком (сгенерировать в Suno, залить на YouTube); во всех остальных
следующий шаг делает Claude.

Внутри папки песни:

```
library/<slug>/
  meta.json                 # стейт: title, slug, stage, source, series, language, created, stage_history
  brief.md                  # бриф: о чём песня
  lyrics.md                 # финальный текст песни
  suno.md                   # промпт для генерации в Suno
  cover-prompt.md           # промпт для генерации обложки
  youtube.md                # заголовок/описание для YouTube
  notes.md                  # свободные заметки
  raw/                      # черновая свалка (старые версии файлов, не в гите)
  cover.jpg | cover.png     # ровно одна обложка (.jpg/.jpeg/.png/.webp) — не в гите
  track.mp3                 # аудиофайл — не в гите
  youtube.mp4               # результат сборки (после build) — не в гите
```

Сборка (`build`) требует в корне папки **ровно один** аудиофайл и **ровно
одну** картинку; лишние варианты складывай в `raw/` (это же делает
`import` автоматически), иначе пайплайн честно откажется угадывать и
попросит навести порядок.

## Команды

```bash
just new "My Track Name"           # создаёт library/my-track-name (stage=idea)
                                   # поддерживает --source, --series, --language

just advance my-track-name         # двигает песню на следующую стадию,
                                   # если для неё готовы нужные файлы

just import my-track ~/Downloads/take.mp3
                                   # кладёт скачанный файл в папку песни под
                                   # каноническим именем (track.mp3 / cover.*),
                                   # прошлый файл того же типа уходит в raw/

just build my-track-name           # собирает youtube.mp4, stage → pre-published
                                   # требует, чтобы песня была на stage=ready
just build-all                     # собирает все песни со stage=ready

# залей youtube.mp4 на YouTube, затем:
just publish my-track-name         # stage → published

just status                        # таблица всех песен, их стадий и чьего хода ждём
just status --json                 # то же самое в JSON
```

Старой команды `ready` больше нет — её заменил `advance`, который сам
проверяет готовность и двигает песню по всем восьми стадиям, а не только
в `ready`.

## Те же команды без just

`just` — это лишь тонкая обёртка над Python-модулем. Всё то же самое:

```bash
python3 -m sovigen.cli new "My Track Name" [--source ...] [--series ...] [--language uk]
python3 -m sovigen.cli advance my-track-name
python3 -m sovigen.cli import my-track-name ~/Downloads/take.mp3
python3 -m sovigen.cli build my-track-name
python3 -m sovigen.cli build-all
python3 -m sovigen.cli publish my-track-name
python3 -m sovigen.cli status [--json]
```

## Структура кода

```
sovigen/
  cli.py            # разбор аргументов и точка входа (argparse)
  commands.py       # логика команд new/advance/import/build/build-all/publish/status
  artifacts.py      # шаблоны md-артефактов и проверка готовности стадии
  templates/         # шаблоны brief.md/lyrics.md/suno.md/cover-prompt.md/youtube.md/notes.md
  ffmpegcmd.py      # сборка ffmpeg-команды для статичного видео
  inputs.py         # поиск ровно одного аудио и одной картинки в папке
  meta.py           # чтение/запись meta.json, восемь стадий, переходы
  paths.py          # расположение library/ и папок песен
  slug.py           # slugify заголовка (Unicode-aware, сохраняет кириллицу)
library/
  <slug>/           # одна папка на песню, см. выше
knowledge/
  README.md         # карта базы: что где лежит и в каком порядке это читать
  role.md           # роль соавтора, два формата, подбор стиля, тон
  craft/            # ремесло по этапам: lyrics, suno, cover, youtube
  styles/           # карточки откалиброванных стилей
  series/           # очередь по сериям (псалмы)
  log.md            # журнал: что сработало в Suno
tests/              # pytest-сьют на каждый модуль
```

## Формат видео

1920×1080, картинка вписана целиком с чёрным padding (ничего не
обрезается), `libx264` / `yuv420p`, аудио `aac 320k`, длительность = длине
песни, `+faststart` для быстрой отдачи. Точная команда — в
`sovigen/ffmpegcmd.py`.

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

- Долговременное и воспроизводимое хранение медиа (mp3/обложки/видео) вне
  гита — открытый вопрос, issue [#1](https://github.com/vladimirfriptu/sovigen/issues/1).
- Оживление обложки через Stable Video Diffusion + бесшовный луп/реверс —
  команды `animate` и `build --render` зарезервированы, но не реализованы.
