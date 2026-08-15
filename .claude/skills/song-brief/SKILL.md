---
name: song-brief
description: Write the briefs for one song — the shared source analysis plus THREE competing variants, each with its own concept, arc and style. Use when a song is at stage `idea`, or when the user says "сделай бриф для <name>", "о чём будет песня по псалму N", "предложи стиль для <name>". Never write lyrics from here.
---

# Write the briefs for a song

Take ONE song from `stage: idea` to `stage: brief`. The output is a filled root
`brief.md` (what all three variants share) plus three `variants/<id>/brief.md`,
and the three variants recorded in `meta.json`.

This skill does **not** stop and ask. Three variants exist precisely so the
owner's single decision can be made on audio, after Suno — see `song`.

## Inputs

The slug of an existing song folder (`library/<slug>/`). If the folder does not
exist yet, that is the `song` orchestrator's job — do not create it here.

Read, and only these:

- `knowledge/role.md` — the two formats, the default, how a style gets chosen.
- `knowledge/styles/references.md` — **the owner's own listening list and the
  order styles must be picked in.** Read it before shortlisting anything.
- `knowledge/styles/antistyles.md` — styles closed by the owner's own words.
  Never propose one, not even as the far pole.
- `knowledge/craft/lyrics.md` — sources, Hebrew numbering, honesty about
  deviations, the "gifts of the text".
- `knowledge/series/<series>.md` for the song's `series` from `meta.json`
  (usually `psalms`) — what is already done and in what style.
- The `knowledge/styles/*.md` cards you shortlist. You need three that differ,
  one per variant; `role.md` has a one-line index to pick from. Do not load all
  eight.

Do not read `knowledge/craft/suno.md` or `knowledge/log.md` here.

## Steps

Create a todo per step and work through them in order.

1. **Read the state.** `library/<slug>/meta.json` → `title`, `source`,
   `series`, `language`, `stage`. If `stage` is not `idea`, the briefs were
   already written: report the current stage and stop instead of overwriting.

2. **Verify the source text against public-domain sources — do not write it
   from memory.** For a psalm: `tehillim-online.com`, Sefaria or `mechon-mamre`.
   Fetch it. Verse numbers are Hebrew numbering (the superscription is verse 1,
   so it is shifted +1 against most Christian editions). Note in the brief
   which source you checked against.

3. **Fill the root `library/<slug>/brief.md`** — only what the three variants
   share. Keep the template's sections; the two that belong to a single reading
   (`## О чём песня`, `## Эмоциональная арка`) move down into the variants.
   - `## Источник` — what text this is and where it was verified.
   - `## Встроенные подарки текста` — repeated verses, refrains, ready-made
     choruses. Shared: they are properties of the psalm, not of a reading.
   - `## Варианты` — the comparison table:

     | Вариант | Стиль | Угол | Приём | Чем не похож на другие |
     |---|---|---|---|---|
     | a | [[styles/…]] | … | … | … |
     | b | … | … | … | … |
     | c | … | … | … | … |

4. **Fill `library/<slug>/variants/<id>/brief.md` for `a`, `b` and `c`.**
   Create the directories yourself — the templates do not scaffold them, and
   `render` never touches anything inside `variants/`. Each file carries:
   - `## О чём песня` — two or three sentences about what happens to a person
     in *this* reading.
   - `## Эмоциональная арка` — from what, to what.
   - `## Стиль` — one `[[styles/<name>]]` link and one or two sentences of why.
     Link the card, do not restate it. No alternatives here: the other two
     variants *are* the alternatives.

5. **Check the three against the divergence rules below.** If two of them fail
   the check, rewrite before going any further — a bad set of three costs three
   texts, not one.

6. **Record the three variants in `meta.json`.** There is no CLI command for
   this field, so write it through the project's own meta module — it normalizes
   the file and keeps every other field intact. Run from the repo root:

   ```bash
   python3 - <<'PY'
   import json, os
   from sovigen import meta, paths

   slug = "<slug>"
   variants = [
       {"id": "a", "style": "<card-stem>", "angle": "<угол>"},
       {"id": "b", "style": "<card-stem>", "angle": "<угол>"},
       {"id": "c", "style": "<card-stem>", "angle": "<угол>"},
   ]

   song_dir = paths.song_dir(slug)
   data = meta.read_meta(song_dir)
   data["variants"] = variants
   target = meta.meta_path(song_dir)
   tmp = target.with_suffix(".json.tmp")
   tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
   os.replace(tmp, target)
   print(target.read_text(encoding="utf-8"))
   PY
   ```

   Style stems are file names (`casting-crowns`), not links
   (`[[styles/casting-crowns]]`). The top-level `style` field stays `null` here —
   `just choose` fills it from the winning variant.

   Never hand-edit `meta.json` with Edit and never rewrite it from scratch:
   that is how `stage_history` gets lost. The temp file plus `os.replace` is
   what keeps a crash mid-write from leaving a truncated `meta.json`.

7. **Verify the variants landed, then advance.** `advance` does not look at
   `variants`, so a silently failed write would leave the song at `brief` with
   nothing recorded — and `song-suno` would have no card to read. Run:

   ```bash
   python3 -c "import json,sys; d=json.load(open('library/<slug>/meta.json')); print([v['id'] for v in d['variants']]); sys.exit(0 if len(d['variants']) == 3 else 1)"
   ```

   If it prints fewer than three ids or exits non-zero, do **not** advance —
   redo step 6 and find out why it failed.

   Only then: `just advance <slug>` → `idea -> brief`. The gate is the root
   `brief.md`; a variant's own `brief.md` deliberately does not satisfy it.

8. **Tell the user, in two or three lines, what the three variants are** — one
   line each: style, angle, device. Then hand straight over to `song-lyrics`.
   Do not ask whether the set is good; the answer to that question is audio,
   and it does not exist yet.

## Как варианты остаются разными

Three costumes on one song are not worth comparing. Every set of three must
satisfy all of these, and the check happens before a single line of lyrics is
written:

- **Pick in the order set by [[styles/references]].** The owner's own listening
  list comes first, then the existing cards, and experiments outside both only
  after the offered variants failed him. A set of three where nothing comes from
  his references is wrong before it is written — that mistake cost seven
  variants on Psalm 10.
- **Different style cards.** Repeating a card inside one song is forbidden.
- **Different angle** — whose eyes the psalm is seen through (the victim, a
  witness, an accuser, the one who waits, …).
- **Different formal device** — e.g. a question-chorus that flips at the end; a
  single verse used as a running refrain; no chorus at all, narrative verses.
- **One variant on the owner's home territory** (intimate, chamber) and **one
  deliberately far from it**. Without this rule all three drift to the safe
  middle.
- If two rows of the comparison table read the same in the «Чем не похож»
  column, rewrite that variant now.

## Guardrails

- Never copy a copyrighted Bible translation (Огиенко, Хоменко, Турконяк).
  The Ukrainian text is an original переспів, close in meaning.
- Never write the psalm text from memory — verify it first.
- There is no gate in the creative half any more. The owner's single decision is
  made on audio, after Suno — see `song`.
- Do not write a single line of lyrics in this skill.
- The user never edits files. You write, they react in words.
- Don't commit anything (project policy: wait for an explicit signal).
