# sovigen — конвейер песен — слой AI-правил проекта

Эта папка коммитится: она и есть рабочий процесс проекта, и без неё
репозиторий, подключённый к claude.ai, не запустится. Общие правила владельца
живут отдельно, в `~/.claude/CLAUDE.md`, и сюда не переезжают.

## Commit and push every iteration

**Каждый заход заканчивается коммитом и пушем.** Не «когда владелец скажет», не
«когда работа выглядит законченной» — всегда, как только сделан связный кусок:
песня продвинулась по стадии, написаны варианты, поправлено правило.

Причина не в аккуратности, а в доступе: владелец открывает `library/` в Obsidian
с телефона, и репозиторий — единственный канал синхронизации. Незапушенная
работа для него просто не существует.

Из этого следует:

- **Рабочее дерево не остаётся грязным в конце ответа.** Если что-то сделано —
  оно закоммичено и запушено до того, как отвечать владельцу.
- **Коммит осмысленный, не «wip».** Владелец читает историю с телефона;
  сообщение должно объяснять, что изменилось и почему.
- **Спеки и планы (`.claude/specs/`, `.claude/plans/`) в коммит не идут** — это
  AI-артефакты. Всё остальное идёт.
- **Медиа не идут** — `.gitignore` пропускает из `library/` только `*.md` и
  `meta.json`. Проверять правило не нужно, но и обходить его нельзя.
- **Репозиторий публичный.** Тексты песен и черновики видны всем, владельца это
  устраивает. Прямое следствие: никаких секретов в файлах проекта.
- Если пуш отклонён (удалённая ветка ушла вперёд) — разобраться, а не
  форсировать. `--force` только по прямой просьбе владельца.

## Knowledge base — read before deciding, not by default

A personal knowledge base lives at `/Users/v.friptu/WebstormProjects/fhome_sb`
(`BRAIN`). It holds the *why* behind this project — reasons, rejected
alternatives, constraints that surfaced earlier — which is exactly what the
repository cannot tell you. It is private to the owner: **never assume anyone
else can see it**, and never cite it as a source in a commit message, a pull
request or a code comment.

**It exists only on the owner's machine.** In any session without that path —
claude.ai connected to this repository, a clone on another machine — the base
is simply absent: skip every instruction below, do not look for a substitute,
and never recreate its files inside this repository. The pipeline works without
it; the base only carries history.

- Project card: `$BRAIN/projects/sovigen.md`
- Router: `$BRAIN/index.md`

**Read the card when** you are about to make or argue an architectural decision,
explain why something here is the way it is, propose replacing or rewriting a
part of the project, or reopen a question that smells settled. In those moments
the card is cheaper than reconstructing the reasoning from `git log` — and more
honest, because it separates recorded reasons from unknowns.

**Do not read it** for ordinary work inside a part you already understand.
Context is finite; loading history that changes nothing wastes it.

### Writing back

One entry point, and nothing else writes to the base from here:

- `/brain-note` — a decision or a trap caught mid-work. Fast, one file, no
  distillation.

It only drops raw material into `$BRAIN/raw/inbox/`. **Never edit a card, the
index, the journal or any other page of the base from this project** — the base
distils its own material, with the whole base in context, and a session here
cannot see what else a page has to agree with.

If the base is unreachable, say so and carry on with the work; do not invent a
fallback file inside this repository.
