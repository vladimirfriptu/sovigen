---
name: release-song
description: Drive a song through the sovigen pipeline from its current state up to the `pre-published` stage, then hand the final video to the user for testing. Use when the user says "погнали для песни <name>", "собери песню <name>", "доведи <name> до предрелиза", "release <name>", or otherwise asks to run a specific song through the release pipeline. STOP at pre-published — never publish automatically.
---

# Release a song to pre-published

Drive ONE song from its current state to `stage: pre-published`, verify the
output, and hand it to the user to test. Do not publish — `publish` is the
user's explicit action after they upload to YouTube.

## Inputs

The user names a song (e.g. "погнали для песни Туман над лесом"). Derive the
slug the same way `slugify` does: lowercase, runs of non-alphanumeric chars
(Unicode-aware, keeps Cyrillic) → single hyphens, trim edge hyphens.

If the user gives a slug directly, use it as-is.

## Steps

Create a todo per step and work through them in order.

1. **Resolve the song folder.**
   - Run `just status` to see existing songs and their stages.
   - Match the named song to a slug under `library/`.
   - If no folder exists: this skill does not create songs — the `song` skill
     owns creation and the whole creative half. Say so and hand over to it.
     Do not run `just new` here and do not invent inputs.

2. **Check the current stage (read `library/<slug>/meta.json`).**
   - `published` → already done; report and stop.
   - `pre-published` → already built; skip to step 5 (re-verify + hand off).
   - `recorded` / `ready` → continue.
   - anything earlier (`idea`, `brief`, `lyrics`, `prompted`) → the song has no
     track yet; hand it to the `song` skill instead.

3. **Verify inputs are present in the song folder root.**
   - Exactly one `*.mp3` and exactly one image (`*.jpg/.jpeg/.png/.webp`)
     directly in `library/<slug>/` (files in `raw/` don't count).
   - If more than one of either: ask WHICH file to keep — that is a choice,
     not a chore — and then do the moving yourself. `just import <slug> <path>`
     installs the keeper under its canonical name and stashes the previous one
     in `raw/` on its own; any remaining stragglers you move into `raw/`.
     Never guess between candidates, and never ask the user to move a file.
   - If none of either: say what is missing. A missing track means the song
     belongs in the `song` skill; a missing cover has no automation in this
     phase, so ask the user for the image and import it yourself once they
     point at it.
   - If `youtube.mp4` already exists but stage isn't `pre-published`:
     ask the user before overwriting (the build refuses silently otherwise).

4. **Build.**
   - If stage is `recorded`, run `just advance <slug>` first — it checks the
     cover and `youtube.md` are there and moves the song to `ready`. (`build`
     itself doesn't require `ready`; only `build-all` filters on it. The old
     `ready` command no longer exists.)
   - Run `just build <slug>`.
   - This runs real ffmpeg and, on success, sets stage to `pre-published`.
   - If ffmpeg fails, surface stderr and stop — stage stays unchanged.
     Treat it as a real bug (use systematic-debugging), don't paper over it.

5. **Verify the output (evidence before claiming success).**
   - `ffprobe -v error -select_streams v:0 -show_entries stream=width,height,pix_fmt -of default=noprint_wrappers=1 library/<slug>/youtube.mp4`
     → expect `1920 / 1080 / yuv420p`.
   - `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1 library/<slug>/youtube.mp4`
     → duration should match the track length.
   - Confirm `meta.json` stage is `pre-published`.

6. **Hand off to the user.**
   - Report path, resolution, and duration.
   - Suggest: `open library/<slug>/youtube.mp4` to test the final result.
   - Remind: after uploading to YouTube, they run `just publish <slug>`.

## Batch variant

If the user says "собери всё что готово" / "погнали всё" — instead of one
song, run `just build-all` (builds every song at stage `ready`), then run
step 5 verification for each slug it reports as built.

## Guardrails

- Never run `just publish` on your own — that's the user's call.
- Never create or rename input files. Missing/ambiguous inputs → ask.
- Don't commit anything (project policy: wait for an explicit signal).
- The Python CLI uses stdlib only, so `python3 -m sovigen.cli` works without
  the venv; the venv is only for `just test`.
