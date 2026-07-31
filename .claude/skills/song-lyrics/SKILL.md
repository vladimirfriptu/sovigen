---
name: song-lyrics
description: Write `lyrics.md` for one song from its accepted `brief.md` — structural tags, the section↔verse table, and an honest note on deviations. Use when a song is at stage `brief`, or when the user says "пиши текст для <name>", "давай слова". Do NOT stop after it — the text is shown to the user together with `suno.md`, so hand straight over to `song-suno`.
---

# Write the lyrics for a song

Take ONE song from `stage: brief` to `stage: lyrics`. The output is a filled
`lyrics.md`.

There is no checkpoint in this skill. The gate was `brief.md`, and the user
already passed it — the lyrics and the Suno prompt are produced back-to-back
and shown together at the end of `song-suno`. Do not stop to show the text on
its own.

## Inputs

The slug of a song whose `brief.md` is written and accepted.

Read, and only these:

- `library/<slug>/brief.md` — the concept, the arc, the gifts of the text, the
  chosen style. This is your spec.
- `knowledge/craft/lyrics.md` — the rules this step must not break.

You do not need `knowledge/craft/suno.md` here — the two files are deliberately
independent. `song-suno` reads it.

## Steps

Create a todo per step and work through them in order.

1. **Read the state.** `library/<slug>/meta.json` → `stage`, `language`,
   `source`. If `stage` is still `idea`, `brief.md` was never accepted: stop
   and send the user to `song-brief`. If `stage` is past `lyrics`, the text
   exists — report and stop instead of overwriting.

2. **Read `brief.md`.** The form is already decided there: the "встроенные
   подарки текста" section tells you what the chorus is before you write a
   line of it. Follow it; if you end up departing from the brief, say so when
   the text is presented.

3. **Re-check the verses you actually use** against the public-domain source
   named in `brief.md`. Hebrew numbering. Do not write the psalm text from
   memory.

4. **Fill `library/<slug>/lyrics.md`.** Keep the template's sections.
   - The text itself, with structural tags — `[Verse 1: intimate]`,
     `[Pre-Chorus]`, `[Chorus: full band]`, `[Bridge: building]`, `[Outro]`.
   - The intro is written as a full line, not as `[Intro]`:
     `[Intro: instrumental only, no vocals]`. Without it Suno sings over the
     intro almost every time.
   - No fillers — «о-о-о», «yeah», «на-на». Suno inflates them into whole
     sections.
   - One language version per file. Ukrainian переспів unless `language` or
     the brief says otherwise. Never lift a copyrighted translation — write
     original lines, close in meaning.
   - `## Соответствие источнику` — the section↔verse(s) table, one row per
     section, verses in Hebrew numbering.
   - `## Насколько близко к тексту` — honest: what you compressed, reordered
     or dropped for the sake of the song's form, and why.

5. **Advance.** `just advance <slug>` → `brief -> lyrics`.

6. **Hand over to `song-suno` immediately.** Do not present the text, do not
   ask a question, do not summarize. The user sees the lyrics and the Suno
   fields in one message, at the end of `song-suno`.

## Guardrails

- No copyrighted Bible translations. Original переспів only.
- Hebrew verse numbering, always.
- Never invent a file structure that contradicts the templates — the form
  lives in `sovigen/templates/`.
- The user never edits files. When they react in words later
  («второй куплет слабый, там нужен образ воды»), you edit `lyrics.md` and
  report what changed.
- Don't commit anything.
