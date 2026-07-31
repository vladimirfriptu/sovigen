---
name: song
description: Drive ONE song through the creative half of the sovigen pipeline — from `idea` through brief, lyrics and the Suno prompt to a downloaded take at `recorded` — resuming from wherever it currently is. Use when the user says "погнали песню по Псалму 9", "продолжим <name>", "что там с <name>", "новая песня", or names a song without saying what to do with it. Resumable: always read the state first, never assume.
---

# Drive a song through the creative pipeline

One song, from wherever it stands to `stage: recorded`. Work can be picked up
days later, so the first move is always to read state — never to assume it.

Stages and who moves next:

```
idea → brief → lyrics → prompted → recorded → ready → pre-published → published
```

`idea`/`brief`/`lyrics` are Claude's turn. `prompted` waits for the human in
Suno. From `recorded` on, the cover and the video are outside this skill —
`release-song` builds the video once a cover and `youtube.md` exist.

## Steps

Create a todo per remaining stage as soon as you know the state, so the path
is visible. Then work through them.

1. **Read the state first.**

   ```bash
   python3 -m sovigen.cli status --json
   ```

   It prints one row per song: `slug`, `stage`, `title`, `turn`. Find the song
   the user means. Derive the slug the way `slugify` does: lowercase, runs of
   non-word characters (Unicode-aware, Cyrillic is kept) → single hyphens,
   trimmed at the edges. If the user gave a slug, use it as-is.

2. **Resolve the song — two cases.**

   **It exists** (a row in `status`): read `library/<slug>/meta.json` for
   `stage`, `style`, `source`, `series`, `stage_history`. Tell the user in one
   line where it stands and what the next step is, then continue from that
   stage in step 4. Never restart a stage that is already behind.

   **It does not exist** (the user names a theme — «песня по Псалму 23» — or a
   title with no folder): the slug is permanent and the folder cannot be
   renamed later, so do not invent a title silently. Propose two or three
   titles in one short message and ask which one. That is a naming question,
   not a content checkpoint — keep it to one message. Then create it:

   ```bash
   just new "<Название>" --source psalm-23 --series psalms
   ```

   `--language` defaults to `uk`. The command creates `library/<slug>/` at
   `stage: idea` with every artifact template already in place.

3. **Glance at the series queue, once per session.** Read
   `knowledge/series/psalms.md`. If the «Очередь» table has fewer than five
   psalms with a filled-in style or note, offer — in one sentence — to top the
   queue up later. Offer only; do not start doing it and do not let it delay
   the song at hand.

4. **Walk the stages, invoking the stage skill for each.**

   | Stage now | What you do |
   |---|---|
   | `idea` | `song-brief` → it STOPS at the concept and waits |
   | `brief` | `song-lyrics`, then immediately `song-suno` — no pause between them |
   | `lyrics` | `song-suno` |
   | `prompted` | step 5 — the user's turn in Suno |
   | `recorded` | step 6 — hand off |

   The only stop inside the creative half is after `brief.md`. `lyrics.md` and
   `suno.md` are written back-to-back and presented together at the end of
   `song-suno`. Do not insert a checkpoint between them.

5. **At `prompted`, wait for the human.** There is no Suno API. Say, in
   Russian: «Генери в Suno и послушай. Как выберешь дубль — скажи какой и
   откуда его скачал, дальше я сам.»

   When the user comes back naming a take:
   - Find the file yourself. It is normally the freshest `.mp3` in
     `~/Downloads`: `ls -t ~/Downloads/*.mp3 | head -5`. If several plausibly
     match, show the candidates with their timestamps and ask which — never
     guess between takes.
   - `just import <slug> <path>` — copies it in as `track.mp3` and moves any
     previous audio into `raw/` on its own. Never move or rename files by hand.
   - `just advance <slug>` → `prompted -> recorded`. It refuses if no audio is
     present, which is the check that the import landed.
   - Moving files is Claude's job. Only three actions belong to the user:
     generating and listening in Suno, choosing a take, and uploading to
     YouTube.

6. **At `recorded`, stop and hand off.** Report what exists. The next stage,
   `ready`, needs a cover image and a filled `youtube.md` — neither is
   automated in this phase. Say what is missing and offer to write `youtube.md`
   from `knowledge/craft/youtube.md` and the cover prompt from
   `knowledge/craft/cover.md`. Once a cover is in the folder, `release-song`
   builds `youtube.mp4`.

## Advancing

`just advance <slug>` moves exactly one stage and only checks that the files
that stage requires exist — and the templates create most of them at `new`. So
the file check is not the gate. Two transitions need the user's word, and only
those two:

| Transition | What authorizes it |
|---|---|
| `idea → brief` | the content gate — an explicit yes to the concept and the style |
| `prompted → recorded` | the user has generated in Suno and named the take |
| `brief → lyrics`, `lyrics → prompted` | nothing extra — bookkeeping inside the block the brief gate already authorized |

Never advance past a content gate or a human action without the user's word.
Do **not** ask for one before `brief → lyrics` or `lyrics → prompted`: those
two files are written back-to-back and shown together, and a question there is
the forbidden extra checkpoint. If the user asks for edits after seeing the
pair, edit the files in place — the stage does not move back, it only asserts
the files exist.

Every transition is appended to `stage_history` in `meta.json`, which is how a
later session can tell what really happened.

## Guardrails

- Read state before acting, every time — this skill is meant to resume.
- One song per run. If the user names several, do them one at a time.
- The user never opens or edits a file. They react in words, you edit and
  report what changed.
- Never run `just publish` — that is the user's call after the upload.
- Never `just build` from here; that is `release-song`.
- The Python CLI is stdlib-only, so `python3 -m sovigen.cli` works without the
  venv. The venv is only for `just test`.
- Don't commit anything (project policy: wait for an explicit signal).
