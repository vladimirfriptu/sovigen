---
name: song-suno
description: Fill `suno.md` for one song — the `Style` and `Exclude Styles` strings plus per-song generation notes — then present the lyrics and both fields together, ready to paste, and stop. Use when a song is at stage `lyrics`, or when the user says "давай промпт для Suno", "готовь стиль". This is where Claude's turn ends and the human goes to Suno.
---

# Write the Suno prompt for a song

Take ONE song from `stage: lyrics` to `stage: prompted`. The output is a filled
`suno.md` and one message the user can copy from into Suno.

This skill normally runs straight after `song-lyrics`, without a pause between
them. The lyrics were never shown on their own — you show them here, together
with the fields.

## Inputs

The slug of a song whose `lyrics.md` is written.

Read, and only these:

- `library/<slug>/lyrics.md` — the text you are generating.
- `knowledge/craft/suno.md` — the two fields and the anti-melisma recipe.
- `knowledge/styles/<style>.md`, where `<style>` is the `style` field in
  `library/<slug>/meta.json` — it holds ready `Style` and `Exclude Styles`
  strings to start from.

You do not need `brief.md`, `knowledge/role.md` or `knowledge/craft/lyrics.md`
here.

If `meta.json` has `style: null`, the brief gate was skipped or the style was
never recorded. Ask the user which style card to use and record it the way
`song-brief` step 6 does — do not guess one.

## Steps

Create a todo per step and work through them in order.

1. **Read the state.** `library/<slug>/meta.json` → `stage`, `style`,
   `language`. If `stage` is not `lyrics`, say where the song actually is and
   stop.

2. **Read the style card** named by `style` and take its `Style` and
   `Exclude Styles` blocks as the base. Extend them for this song — do not
   rewrite them from scratch, the cards are calibrated.

3. **Fill `library/<slug>/suno.md`.** Keep the template.
   - Frontmatter `style:` — the style card stem, matching `meta.json`.
   - `## Style` — one English string. It must positively describe the vocal:
     `clean straight-tone vocal, syllabic delivery (one note per syllable),
     restrained on-the-beat phrasing, no runs, no ad-libs`. Add the BPM and
     the feel (4/4, 6/8) that fit this psalm's mood — the meter decides
     whether the song sways or marches. Avoid the trigger words `worship` and
     `spontaneous`; use `contemporary Christian ballad` or `pop-rock ballad`
     instead — they pull melismas along by themselves.
   - `## Exclude Styles` — one English string, including
     `melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh
     chants, spontaneous worship, oversinging, vocal improvisation`, plus
     whatever this style card excludes.
   - `## Советы по генерации` — what matters for *this* song: tempo, meter,
     expected length, what to watch for in the vocal, and what to do if Suno
     cuts it (drop one `[Chorus]` repeat, or generate in two passes and
     splice). Roughly 3 minutes is the safe length.

4. **Check the lyrics against the recipe** while you are here: is the intro
   written as `[Intro: instrumental only, no vocals]`, are there any fillers
   left? If something is off, fix `lyrics.md` — it is cheaper now than after
   a bad take.

5. **Advance.** `just advance <slug>` → `lyrics -> prompted`. `prompted` is a
   human-turn stage: from here the pipeline waits for a person.

6. **Present everything in one message, then stop.**
   - The full lyrics, verbatim, in a code block — this is what goes into
     Suno's Lyrics field.
   - The `Style` string in its own code block.
   - The `Exclude Styles` string in its own code block.
   - Two or three lines of the generation notes.
   - Then, in Russian: «Текст и оба поля готовы — генери в Suno и послушай.
     Как выберешь дубль, скажи какой и где лежит файл — я его положу в папку
     песни сам.»
   - Stop. There is no Suno API: generating and listening is the user's
     manual action, and so is choosing a take.

7. **If the user comes back with edits** («второй куплет слабый, там нужен
   образ воды», «слишком быстро») — edit `lyrics.md` or `suno.md` yourself,
   report what changed, and present the affected block again. The stage stays
   at `prompted`; it only asserts that the files exist. Never tell the user to
   open or edit a file.

## Guardrails

- Both fields are always filled, both always in English, even when the lyrics
  are Ukrainian.
- One language version in the Lyrics field. Latin transliteration only on
  request, as a separate block.
- Do not run `just import` or `just advance` past `prompted` here — moving to
  `recorded` needs a real `track.mp3`, which only exists after the user has
  generated and picked a take.
- Don't commit anything.
