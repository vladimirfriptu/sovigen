# Knowledge base

Everything the creative steps of the pipeline need to know before they write
anything. The CLI owns folders, stages and file checks; this folder owns the
craft.

The subject content is in Russian, matching how the owner works. Song-facing
English strings (Suno `Style` / `Exclude Styles`, cover prompts) stay English —
that is what gets pasted into the tools.

## What lives where

| File | What it holds |
|---|---|
| [[role]] | Who the co-author is, the two output formats, the default, how a style gets chosen, tone. |
| `craft/` | One file per creative step — the rules that step must not break. |
| [[craft/lyrics]] | Working with the psalm text: sources, numbering, honesty about deviations, structural tags. |
| [[craft/suno]] | The `Style` / `Exclude Styles` fields and the anti-melisma recipe. |
| [[craft/cover]] | The cover-art prompt: 16:9, safe margins, no text. |
| [[craft/youtube]] | Title, description and tag conventions for the channel. |
| `styles/` | One card per calibrated style — mood, ready `Style` and `Exclude Styles` strings, when to reach for it. |
| `series/` | The queue per series: which psalm is done, which is next, in what style. |
| [[log]] | Running log of what actually worked in Suno. Appended after a song is finished, not before. |

## Reading order for a skill

Each skill reads narrowly — do not load the whole base.

| Step | Read |
|---|---|
| `song-brief` | [[role]], [[craft/lyrics]], the relevant `series/` file, the candidate `styles/` cards |
| `song-lyrics` | the song's `brief.md`, [[craft/lyrics]] |
| `song-suno` | the song's `lyrics.md`, [[craft/suno]], the `styles/` card named in `meta.json` |
| cover | [[craft/cover]] |
| publication | [[craft/youtube]] |
| retro | [[log]], the `styles/` card used, the song's `notes.md` |

[[craft/lyrics]] and [[craft/suno]] are deliberately independent: neither needs
the other to be usable.

## How it grows

Style cards and the series queue are living documents. After a song is
released, the retro appends to [[log]] and updates the "Где применялся"
section of the style card that was used. New craft rules go into the `craft/`
file of the step they belong to — not into a song folder, where they would be
lost after that song.
