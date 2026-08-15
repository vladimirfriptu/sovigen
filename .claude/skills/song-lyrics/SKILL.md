---
name: song-lyrics
description: Write the lyrics for all three variants of one song from their briefs — structural tags, the section↔verse table, and an honest note on deviations, one file per variant. Use when a song is at stage `brief`, or when the user says "пиши текст для <name>", "давай слова". Do NOT stop after it — the texts are shown to the user together with the Suno prompts, so hand straight over to `song-suno`.
---

# Write the lyrics for a song

Take ONE song from `stage: brief` to `stage: lyrics`. The output is three filled
`variants/<id>/lyrics.md` — never a root `lyrics.md`. The root file is a copy of
the winner, and only `just choose` writes it.

There is no checkpoint in this skill and none after it. The owner's single
decision is made on audio: he generates all three in Suno, listens, and picks.
So the three texts and the three prompts are produced back-to-back and presented
together at the end of `song-suno`.

## Inputs

The slug of a song whose briefs are written.

Read, and only these:

- `library/<slug>/brief.md` — the shared analysis and the comparison table.
- `library/<slug>/variants/<id>/brief.md` for all three — each is the spec for
  its own text.
- `knowledge/craft/lyrics.md` — the rules this step must not break.

You do not need `knowledge/craft/suno.md` here — the two files are deliberately
independent. `song-suno` reads it.

## Steps

Create a todo per variant and work through them in order.

1. **Read the state.** `library/<slug>/meta.json` → `stage`, `language`,
   `source`, `variants`. If `stage` is still `idea`, the briefs were never
   written: stop and send the user to `song-brief`. If `stage` is past `lyrics`,
   the texts exist — report and stop instead of overwriting. If `variants` is
   empty, this song was started under the old single-variant flow: say so and
   write one root `lyrics.md` the old way rather than guessing.

2. **Read the root `brief.md` and all three variant briefs.** The form of each
   text is already decided in its variant brief — the angle, the arc, the
   formal device. Follow them; if you end up departing from one, say so when the
   texts are presented.

3. **Re-check the verses you actually use** against the public-domain source
   named in the root `brief.md`. Hebrew numbering. Do not write the psalm text
   from memory.

4. **Write `variants/<id>/lyrics.md` for `a`, `b` and `c`, one at a time.**
   Keep the template's sections in each — including the section↔verse table and
   `## Насколько близко к тексту`. Each variant departs from the source
   differently, and that per-variant record is the honest part.
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

5. **Before starting each variant, re-read the comparison table.** The failure
   mode of this step is convergence: variant `c` quietly adopting `a`'s images
   because they are already in your context. A different angle means different
   vocabulary and different line lengths, not the same lines re-broken. If two
   finished texts share their strongest image, one of them is wrong — rewrite it
   now, not after the owner has burned three Suno generations on it.

6. **Advance.** `just advance <slug>` → `brief -> lyrics`. The gate is satisfied
   by a variant file; no root `lyrics.md` is needed.

7. **Hand over to `song-suno` immediately.** Do not present the texts, do not
   ask a question, do not summarize. The user sees all three texts and all three
   pairs of Suno fields in one message, at the end of `song-suno`.

## Guardrails

- No copyrighted Bible translations. Original переспів only.
- Hebrew verse numbering, always.
- Never write a root `lyrics.md` — that file belongs to `just choose`.
- Never invent a file structure that contradicts the templates — the form
  lives in `sovigen/templates/`.
- The user never edits files. When they react in words later
  («второй вариант слабый, там нужен образ воды»), you edit that variant's
  `lyrics.md` and report what changed.
- **Commit and push when the stage is done** — every iteration ends in the
  remote, because the owner reads `library/` in Obsidian on his phone and the
  repository is the only sync channel. See the project `CLAUDE.md`.
