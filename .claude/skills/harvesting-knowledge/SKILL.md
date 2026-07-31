---
name: harvesting-knowledge
description: Use when a piece of work in this project is finished and its local AI artifacts (specs, plans, scratch notes) are about to be deleted — exports them plus a generated decisions document into the knowledge base inbox. Also use before abandoning a branch or wiping a worktree.
---

# Harvesting knowledge into the brain

Export what a finished piece of work knows into the knowledge base **before**
anything is deleted. This skill only collects raw material — it never edits
pages, cards or the index. Distillation happens inside the base (`/ingest`,
`/reflect`), where the whole base is in context.

## Constants

- `BRAIN` = `/Users/v.friptu/WebstormProjects/fhome_sb`
- `INBOX` = `$BRAIN/raw/inbox`
- `TODAY` = `date +%F`
- `SOURCE` = `sovigen`

## Target

Resolve and print before doing anything:

- `SCOPE` — what is being harvested, as a kebab-case slug: the branch name, the
  feature, or what the owner named. It goes into filenames, so keep it short and
  recognisable a month from now.
- `RANGE` — the commits this work is made of (`git log --oneline <base>..HEAD`,
  or the last N commits if the work went straight onto the main branch).

If the caller already resolved these, take them as given.

## Gate

If `$BRAIN` is not readable, stop immediately, report `FAILED` with the reason,
and tell the caller that **the artifacts must not be deleted**. Losing the source
is worse than a dirty working tree.

## Never overwrite, never skip

This skill is additive. Running it twice on the same work must not lose the
earlier harvest and must not silently stop — a duplicate costs `/reflect` a few
minutes, a lost harvest costs the reasoning forever.

Before writing anything, look for earlier harvests of this scope:

```bash
grep -rl "^source: $SOURCE$" "$INBOX" "$BRAIN/raw/processed" 2>/dev/null \
  | xargs grep -l "$SCOPE" 2>/dev/null
```

- **Nothing found** — normal run, names as below.
- **Found** — this is a re-harvest. Say so up front and list what was found.
  Write the decisions document as
  `$TODAY-$SOURCE-$SCOPE-decisions-addendum-N.md` (`N` = next free number),
  never as `-decisions.md`.
- **A target filename already exists** — append `-2`, `-3`, … Never write over
  an existing file, not even one this skill wrote a minute ago.

A re-harvest that repeats an earlier one is fine — say so in the document and
name that file. Deciding what is new is `/reflect`'s job, not this skill's.

## Step 1 — collect the evidence

Copy into `$INBOX`, each with the frontmatter below:

| Source | Target name | `kind` |
|---|---|---|
| `.claude/specs/*` matching `SCOPE` | `$TODAY-$SOURCE-$SCOPE-spec-<orig>.md` | `spec` |
| `.claude/plans/*` matching `SCOPE` | `$TODAY-$SOURCE-$SCOPE-plan-<orig>.md` | `plan` |

Match narrowly. If `.claude/` is shared between worktrees, a wide match sweeps
another piece of work's in-progress artifacts into the base.

Frontmatter prepended to every exported file:

```yaml
---
source: sovigen
task: '-'
kind: spec
captured: YYYY-MM-DD
---
```

## Step 2 — write the decisions document

Create `$INBOX/$TODAY-$SOURCE-$SCOPE-decisions.md` (`kind: decisions`). This is
the main artifact — the evidence above exists to check it against.

Read, in this order:

1. **Commit messages over the range, and their bodies.** With no review threads
   in this project, the commit body is the richest surviving record of "why" —
   read it, not just the subject line.
2. The diff stat, for what the work actually touched.
3. The specs and plans collected above — and compare them against what was
   built. **Where the plan and the result disagree, the reason is usually the
   most valuable thing in the whole harvest**: something was learned mid-way.
4. Any `$INBOX/*-note.md` whose `source` is `sovigen` and which belongs to this
   work — notes captured by `/brain-note` while it was running. Fold in what
   belongs, leave the rest alone, and say in the document that they were folded.
   Do **not** delete them; `/reflect` moves them to `processed/` with everything
   else.

Write in **Russian**, short and structured:

```markdown
## Решения

- **Что решили.** Почему именно так. Что рассматривали и отвергли и по какой
  причине. Ссылка на файл или хеш коммита.

## Грабли

- **На что наткнулись.** Неочевидная причина. Как обошли.

## Ограничения, вскрывшиеся в работе

## Открытые вопросы
```

Hard rules:

- **Only what changes a future decision.** A reason, a rejected alternative, a
  constraint that surfaced, a trap with a non-obvious cause. What was done is
  already in `git log` and must not be restated here.
- **Do not restate the README either.** If this project documents its own "why"
  in the repository, that text is already available to any future session — the
  harvest carries what the README leaves out.
- **Invent nothing.** If the commits show "moved from X to Y" but not why, that
  is a line under «Открытые вопросы», not under «Решения». A plausible
  reconstruction recorded as fact is the worst thing that can happen to this
  base.
- **No secrets** — no tokens, keys, passwords, credentialed URLs.
- If nothing passes the filter, do not write the file. Report `NOTHING`. Most
  work is like this and that is fine.

## Step 3 — commit in the base

```bash
git -C "$BRAIN" add raw/inbox
git -C "$BRAIN" commit -m "Import sovigen <scope> artifacts into the inbox"
```

Never push — that is the owner's call. If the base has a dirty tree from another
session, do not stage it wholesale: stage only `raw/inbox`, and say in the report
that other changes were left alone.

## Report

Print one of:

- `EXPORTED` — the files written and the base commit hash. If this was a
  re-harvest, say so and name the earlier files.
- `NOTHING` — nothing passed the filter; no files written. Artifacts are safe to
  delete.
- `FAILED` — the reason. **Artifacts must not be deleted.**
