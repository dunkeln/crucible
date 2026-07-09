---
name: crucible
description: Use when Codex should turn existing project work or data sources into verifier-backed Crucible tasks, run attempts, inspect evidence, or promote learning rows.
---

# Crucible

No reward without a verifier.

Resolve the bundled CLI at `../../crucible` relative to this `SKILL.md`. Use that path as `<crucible>`.

Start from the smallest existing state.

```bash
<crucible> next operator --pack .crucible/pack.lock.json --project <project>
```

Use Crucible as a harness worker, not a general helper.

Loose prose is intent, not permission to rediscover the repo.

1. If `.crucible/pack.lock.json` exists, run `next` before reading task files.
2. Treat the `next` brief as working memory.
3. Edit only files listed by an operator brief.
4. Read full traces only when the brief points to failed evidence.
5. Run the listed harness check before reporting success.
6. Never promote without a passing verifier and teacher repair.

If no pack exists, inspect the project shape once, name the seam, and create the smallest recipe pack around what exists.

Fast paths:

```bash
<crucible> next researcher --pack .crucible/pack.lock.json --project <project>
<crucible> next operator --pack .crucible/pack.lock.json --project <project> --task <task>
<crucible> recipe-pack <task-dir>... --output-root .crucible/tasks --pack .crucible/pack.lock.json
<crucible> run-pack <pack-path> --project <project>
<crucible> list-runs --project <project> --limit 5
<crucible> summarize-run .crucible/projects/<project>/runs/<run_id>
```

Use full JSON only when debugging a run.

When intent is missing, ask in numbered Markdown options. One task per turn; choose the first failed task unless the user names another.

Do not assume `data/`, `metadata.json`, `task.md`, or `verifier.yaml` already exist. Generate recipe artifacts around the source that exists.

Keep verifier, reward, rubric, and judge code in the user's project workspace.
