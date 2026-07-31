---
description: Capture a decision or a trap into the knowledge base inbox, without leaving the work
argument-hint: [what happened, in a sentence or two]
---

Capture this into the knowledge base inbox: $ARGUMENTS

Be fast. Do not read the knowledge base structure, do not edit any page, do not
distil. One file, then get out of the way — the owner is in the middle of
something.

1. Pick a short kebab-case `slug` from what was said.
2. Write
   `/Users/v.friptu/WebstormProjects/fhome_sb/raw/inbox/<YYYY-MM-DD>-sovigen-<slug>-note.md`.
   If that file already exists, append `-2`, `-3`, … — never overwrite an
   existing note, even one written minutes ago on the same slug.

```markdown
---
source: sovigen
task: '-'
kind: note
captured: YYYY-MM-DD
---

# <одна фраза, что произошло>

<Что случилось и почему решили так. По-русски. Ссылка на файл или хеш коммита,
если есть. Ничего не выдумывать: чего владелец не сказал, того в файле нет.>
```

`task` stays `-`: this project has no issue codes, and `task` is what groups
files into one unit of knowledge during consolidation. Inventing a code there
merges unrelated notes.

3. Commit in the base, staging only the inbox:

```bash
git -C /Users/v.friptu/WebstormProjects/fhome_sb add raw/inbox
git -C /Users/v.friptu/WebstormProjects/fhome_sb commit -m "Add note from sovigen"
```

Never push — that is the owner's call. If the base has uncommitted changes from
another session, do not stage them: the command above stages `raw/inbox` only.

4. Report the path in one line. Nothing else — no summary, no suggestions.

If the base is unreachable, say so in one line and do nothing else. Do not
create a fallback file inside this repository.
