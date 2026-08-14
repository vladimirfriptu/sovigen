---
name: song-suno
description: Fill `variants/<id>/suno.md` for all three variants of one song — the `Style` and `Exclude Styles` strings plus per-variant generation notes — then present all three texts and both fields of each, ready to paste, and stop. Use when a song is at stage `lyrics`, or when the user says "давай промпт для Suno", "готовь стиль". This is where Claude's turn ends and the human goes to Suno.
---

# Write the Suno prompts for a song

Take ONE song from `stage: lyrics` to `stage: prompted`. The output is three
filled `variants/<id>/suno.md` and one message the user can copy from into Suno
three times.

This skill normally runs straight after `song-lyrics`, without a pause between
them. The texts were never shown on their own — you show them here, together
with the fields.

## Inputs

The slug of a song whose variant lyrics are written.

Read, and only these:

- `library/<slug>/variants/<id>/lyrics.md` for all three — the texts you are
  generating.
- `library/<slug>/variants/<id>/brief.md` for all three — each names that
  variant's style card.
- `knowledge/craft/suno.md` — the two fields and the anti-melisma recipe.
- The three `knowledge/styles/<style>.md` cards named by the variants — they
  hold ready `Style` and `Exclude Styles` strings to start from.

You do not need the root `brief.md`, `knowledge/role.md` or
`knowledge/craft/lyrics.md` here.

If `meta.json` has an empty `variants` list, this song was started under the old
single-variant flow: say so and fill the root `suno.md` the old way rather than
guessing. If `variants` is filled but an entry has no `style`, ask which card to
use — do not pick one.

## Steps

Create a todo per variant and work through them in order.

1. **Read the state.** `library/<slug>/meta.json` → `stage`, `variants`,
   `language`. If `stage` is not `lyrics`, say where the song actually is and
   stop.

2. **Read each variant's style card** and take its `Style` and `Exclude Styles`
   blocks as that variant's base. Extend them for the variant — do not rewrite
   them from scratch, the cards are calibrated.

3. **Fill `variants/<id>/suno.md` for `a`, `b` and `c`.** Keep the template.
   - Frontmatter `style:` — that variant's card stem. The three differ by
     construction; if two match, `song-brief` broke its own rule and the set
     needs fixing before generation.
   - `## Style` — one English string. It must positively describe the vocal:
     `clean straight-tone vocal, syllabic delivery (one note per syllable),
     restrained on-the-beat phrasing, no runs, no ad-libs`. Add the BPM and the
     feel (4/4, 6/8) that fit this variant — the meter decides whether the song
     sways or marches, and two variants of the same psalm should not share it.
     Avoid the trigger words `worship` and `spontaneous`; use
     `contemporary Christian ballad` or `pop-rock ballad` instead — they pull
     melismas along by themselves.
   - `## Exclude Styles` — one English string, including
     `melisma, vocal runs, vocal riffs, ad-libs, ooohs and aaahs, whoa-oh
     chants, spontaneous worship, oversinging, vocal improvisation`, plus
     whatever this variant's style card excludes.
   - `## Советы по генерации` — what matters for *this* variant: tempo, meter,
     expected length, what to watch for in the vocal, what to do if Suno cuts
     it (drop one `[Chorus]` repeat, or generate in two passes and splice).
     Roughly 3 minutes is the safe length. Name the one thing that would make
     this variant a failed take, so the user can stop listening early.

4. **Do not write the `style` field in `meta.json`.** `just choose` sets it from
   the winning variant. Writing it here would claim a decision that has not been
   made yet.

5. **Check the lyrics against the recipe** while you are here, in all three
   variants: is the intro written as `[Intro: instrumental only, no vocals]`,
   are there any fillers left? If something is off, fix that
   `variants/<id>/lyrics.md` — it is cheaper now than after a bad take.

6. **Advance.** `just advance <slug>` → `lyrics -> prompted`. `prompted` is a
   human-turn stage: from here the pipeline waits for a person.

7. **Present everything in one message, then stop.** Three blocks, `a`, `b`,
   `c`, each built the same way:
   - a one-line header naming the style and the angle — that is how the user
     knows what he is about to hear;
   - the full lyrics of that variant, verbatim, in a code block — this is what
     goes into Suno's Lyrics field;
   - its `Style` string in its own code block;
   - its `Exclude Styles` string in its own code block;
   - one or two lines of its generation notes.

   Close with, in Russian: «Три варианта готовы. Сгенери каждый в Suno,
   послушай и скажи, какой берём и где лежит файл — остальное я сделаю сам.»

   Stop. There is no Suno API: generating and listening is the user's manual
   action, and so is choosing.

8. **If the user comes back with edits** («второй вариант слишком быстрый», «в
   третьем припев не тот») — edit that variant's `lyrics.md` or `suno.md`
   yourself, report what changed, and present the affected block again. The
   stage stays at `prompted`; it only asserts that the files exist. Never tell
   the user to open or edit a file.

## Guardrails

- Both fields are always filled for every variant, always in English, even when
  the lyrics are Ukrainian.
- One language version in the Lyrics field. Latin transliteration only on
  request, as a separate block.
- Never write a root `suno.md` — that file belongs to `just choose`.
- Do not run `just choose`, `just import` or `just advance` past `prompted`
  here — the choice is the user's, and `recorded` needs a real `track.mp3`.
- Don't commit anything.
