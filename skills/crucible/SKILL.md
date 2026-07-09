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

1. Inspect the user's project shape before assuming files.
2. Name the seam: harness, ingress adapter, demo surface, or task/verifier corpus.
3. Prefer an existing pack before rediscovering tasks.
4. Use `next` for follow-up turns so Codex edits from a compact brief.
5. Run the harness before reporting success.
6. Never promote without a passing verifier and teacher repair.

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

When intent is missing, ask in numbered Markdown options.

Do not assume `data/`, `metadata.json`, `task.md`, or `verifier.yaml` already exist. Generate recipe artifacts around the source that exists.

Keep verifier, reward, rubric, and judge code in the user's project workspace.
