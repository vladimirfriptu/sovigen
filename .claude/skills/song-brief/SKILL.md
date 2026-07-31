---
name: song-brief
description: Write `brief.md` for one song — the concept, the emotional arc, the verse gifts, and the chosen style — then STOP and wait for the user to accept it. Use when a song is at stage `idea`, or when the user says "сделай бриф для <name>", "о чём будет песня по псалму N", "предложи стиль для <name>". This is the ONE content gate of the pipeline: never write lyrics from here.
---

# Write the brief for a song

Take ONE song from `stage: idea` to `stage: brief`. The output is a filled
`brief.md` and a style recorded in `meta.json`. This is the single place in the
pipeline where the work stops and waits for the user — the concept and the
style are where the most expensive mistake lives.

## Inputs

The slug of an existing song folder (`library/<slug>/`). If the folder does not
exist yet, that is the `song` orchestrator's job — do not create it here.

Read, and only these:

- `knowledge/role.md` — the two formats, the default, how a style gets chosen.
- `knowledge/craft/lyrics.md` — sources, Hebrew numbering, honesty about
  deviations, the "gifts of the text".
- `knowledge/series/<series>.md` for the song's `series` from `meta.json`
  (usually `psalms`) — what is already done and in what style.
- Only the `knowledge/styles/*.md` cards you actually shortlist — normally
  three. Do not load all eight; `role.md` has a one-line index to pick from.

Do not read `knowledge/craft/suno.md` or `knowledge/log.md` here.

## Steps

Create a todo per step and work through them in order.

1. **Read the state.** `library/<slug>/meta.json` → `title`, `source`,
   `series`, `language`, `stage`. If `stage` is not `idea`, the brief was
   already written: report the current stage and stop instead of overwriting.

2. **Verify the source text against public-domain sources — do not write it
   from memory.** For a psalm: `tehillim-online.com`, Sefaria or `mechon-mamre`.
   Fetch it. Verse numbers are Hebrew numbering (the superscription is verse 1,
   so it is shifted +1 against most Christian editions). Note in the brief
   which source you checked against.

3. **Fill `library/<slug>/brief.md`.** Keep the template's sections and order —
   the artifact templates hold the form across songs, do not invent a new one.
   - `## Источник` — what text this is and where it was verified.
   - `## О чём песня` — two or three sentences about what happens to a person
     here.
   - `## Эмоциональная арка` — from what, to what.
   - `## Встроенные подарки текста` — repeated verses, refrains, ready-made
     choruses. These decide the song's form before the style does.
   - `## Стиль` — the chosen style as a `[[styles/<name>]]` link, one or two
     sentences of why, plus two alternatives with a different accent each.
     Link the cards, do not restate them. Remember the owner's leaning:
     intimate and chamber over grand orchestral pathos.

4. **Show the concept to the user in the chat — as bullet points, not the
   file.** Five or six lines: what the song is about, the arc, the gifts of
   the text, the proposed style and the two alternatives with the reason for
   each. The user reads the message, not `brief.md`.

5. **STOP.** Ask plainly, in Russian: «Годится концепция и стиль? Или менять?»
   Then wait. Do not write lyrics, do not touch `meta.json`, do not advance.
   - If the user reacts in words («арка слабая», «давай интимный фолк»,
     «второй абзац не про то») — you edit `brief.md`, then say what changed
     and ask again. Never ask the user to open or edit the file themselves.
   - Only an explicit yes («ок», «годится», «погнали») opens the next step.

6. **Record the chosen style in `meta.json`.** There is no CLI command for the
   `style` field, so write it through the project's own meta module — it
   normalizes the file and keeps every other field intact. Run from the repo
   root, and substitute the slug and the style card's file stem (e.g.
   `casting-crowns`, not `[[styles/casting-crowns]]`):

   ```bash
   python3 - <<'PY'
   import json, os
   from sovigen import meta, paths

   slug = "<slug>"
   style = "<style-card-stem>"

   song_dir = paths.song_dir(slug)
   data = meta.read_meta(song_dir)
   data["style"] = style
   target = meta.meta_path(song_dir)
   tmp = target.with_suffix(".json.tmp")
   tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
   os.replace(tmp, target)
   print(target.read_text(encoding="utf-8"))
   PY
   ```

   Never hand-edit `meta.json` with Edit and never rewrite it from scratch:
   that is how `stage_history` gets lost. The temp file plus `os.replace` is
   what keeps a crash mid-write from leaving a truncated `meta.json`.

7. **Verify the style landed, then advance.** `advance` does not look at
   `style`, so a silently failed write would leave the song at `brief` with
   `style: null` — and `song-suno` would then have no card to read. Check the
   read-back the script printed in step 6, or run:

   ```bash
   python3 -c "import json,sys; d=json.load(open('library/<slug>/meta.json')); print(d['style']); sys.exit(0 if d['style'] else 1)"
   ```

   If it prints `None` or exits non-zero, do **not** advance — redo step 6 and
   find out why it failed.

   Only then: `just advance <slug>` → `idea -> brief`.
   `advance` only checks that `brief.md` exists (the template put it there on
   `new`), so the check that matters is the user's yes in step 5 — never run it
   before that.

## Guardrails

- Never copy a copyrighted Bible translation (Огиенко, Хоменко, Турконяк).
  The Ukrainian text is an original переспів, close in meaning.
- Never write the psalm text from memory — verify it first.
- One gate, here. Do not add a second one later in the pipeline.
- Do not write a single line of lyrics in this skill.
- The user never edits files. You write, they react in words.
- Don't commit anything (project policy: wait for an explicit signal).
