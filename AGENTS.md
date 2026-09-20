# Codex compatibility entry point

This repository's canonical project instructions live in `.claude/`. They are
shared by Claude Code and Codex; do not fork or duplicate their rules here.

Before doing any work in this repository:

1. Read `.claude/CLAUDE.md` in full and follow it as the project-level
   instruction file.
2. Read `README.md` for the current pipeline and command surface.
3. Read state before acting. For song work, start with
   `python3 -m sovigen.cli status --json` and the target song's `meta.json`.

## Workflow routing

When a request matches one of these workflows, read the referenced file in full
before acting and follow it as the task-specific procedure:

- Create or resume a song through the creative pipeline:
  `.claude/skills/song/SKILL.md`
- Write the shared brief and three variant briefs:
  `.claude/skills/song-brief/SKILL.md`
- Write lyrics for the three variants:
  `.claude/skills/song-lyrics/SKILL.md`
- Write the three Suno prompt sets:
  `.claude/skills/song-suno/SKILL.md`
- Build a recorded song through `pre-published`:
  `.claude/skills/release-song/SKILL.md`
- Capture a private knowledge-base note:
  `.claude/commands/brain-note.md`
- Turn private knowledge-base action orders into GitHub issues:
  `.claude/commands/brain-actions.md`

If a workflow hands off to another workflow, read the next workflow file before
continuing. Treat `.claude/specs/` and `.claude/plans/` as historical design
artifacts: consult them when relevant, but obey the current code, README, and
workflow files when they differ.

## Environment differences

- The private `BRAIN` path mentioned in `.claude/CLAUDE.md` and the two brain
  commands exists only on the owner's machine. If it is absent, follow the
  documented rule: report that it is unavailable and do not create a fallback.
- Suno generation/listening and YouTube upload remain human actions. Never
  claim they were performed without access and evidence.
- Media are intentionally ignored by Git. Never bypass `.gitignore` to commit
  audio, cover images, raw takes, or rendered video.

