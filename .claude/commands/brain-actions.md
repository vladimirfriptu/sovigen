---
description: Pick up this project's open action orders from the knowledge base and hand them off into GitHub Issues
argument-hint: [optional path to a specific order file]
---

Execute the sovigen items from the knowledge base action orders: $ARGUMENTS

The base (`BRAIN` = `/Users/v.friptu/WebstormProjects/fhome_sb`) writes orders but
never touches a tracker — every project runs its own flow. This command is that
flow for **sovigen — конвейер песен**, and its tracker is **GitHub Issues of this repository**.

## 1. Collect

If no path was given, list `$BRAIN/meetings/actions/*.md` — **that glob only, no
recursion** — with `status: open`, and read the `## sovigen` section of each.
Ignore sections for other projects entirely: they are not yours to execute or to
mark done.

Do not descend into `$BRAIN/meetings/actions/done/`. Those are finished and their
knowledge is already distilled; reading them wastes context and risks
re-executing settled items.

If there are no open sovigen items, say so in one line and stop.

## 2. Verify before acting

Each item names who asked for it and where it came from (`source:` in the
frontmatter). Read that source and confirm the item matches it. An order is a
distillation; filing an issue makes it real, so check the claim rather than trust
it.

Flag, do not execute, when:

- the source does not support the item, or supports something narrower;
- the item says "create a task" but an equivalent issue already exists — check
  with `gh issue list --search`;
- the item assumes a file, command or constraint that no longer exists here.

**That last case is the most valuable thing this command produces.** The base
cannot check itself against the project; you can. See step 5.

## 3. Show the plan and wait

List what you are about to do, one line per item: create issue / comment on
`#N` / nothing, with the reason. **Do not create anything before the owner
confirms.**

Two reasons this gate is not a formality here:

- **This repository is public.** An issue is world-readable the moment it exists,
  and deleting it later does not undo that.
- The order is written in the base's voice, for the base's reader. It is not the
  text of the issue.

## 4. Execute

`gh issue create --title … --body …` in this repository.

Rewrite the item **in the project's own terms**:

- state the problem and what a solution has to satisfy — that is what the order
  actually carries and what is worth keeping;
- **never paste the order verbatim** and never quote the base. No path to
  `$BRAIN`, no mention of a private knowledge base, no home-directory paths, no
  meeting names, no colleagues' names, no client names. A reader of this
  repository must be able to act on the issue without any of that;
- no secrets, tokens or credentialed URLs — the usual rule, sharper here because
  the repository is public.

If the item is genuinely unclear without base context, that is a signal the
order was written badly: say so, skip the item, and record it in step 5 instead
of publishing a confusing issue.

## 5. Write back into the order

For each executed item: tick the checkbox and append the issue URL.

**Ticked means handed off, not finished.** The issue exists — that closes the
item, even though the work has not started. The base is not a second tracker: it
carries no statuses and no due dates, and nothing here is ever reopened because
an issue is still open. Do not come back to update the order as work progresses.

When every item in **every** project section of the file is ticked, set
`status: done` in the frontmatter. **Then stop — do not move the file.**
Archiving it into `meetings/actions/done/` is the base's job (`/reflect`), and it
happens only after the knowledge inside has been pulled into a card. You cannot
know whether that happened, so a `done` order left in place is correct.

Before finishing, write down anything execution taught you that the order got
wrong or did not know — the base has no other way to learn it:

- **the order's wording was wrong** — say plainly what is actually true. This is
  the only outside check the base gets on itself;
- **the item was a duplicate** — name the existing issue and what it covers;
- **a constraint you had to establish** to file the task at all.

Put it in the item's block, under the tick. Do not edit any card — just record it
where `/reflect` will find it.

Commit in the base, staging only the order file:

```bash
git -C /Users/v.friptu/WebstormProjects/fhome_sb add meetings/actions
git -C /Users/v.friptu/WebstormProjects/fhome_sb commit -m "Close sovigen items from the <date> order"
```

Never push. Never edit any other page of the base from this session — cards, the
journal and the index belong to the base's own commands.

## Report

In Russian: what was created (with issue numbers and URLs), what was skipped and
why, what you recorded back into the order, and whether the order is now closed.
