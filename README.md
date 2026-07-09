<p align="center">
  <picture>
    <img src="assets/logo.png" width="160" alt="Crucible logo" style="border-radius: 28px;" />
  </picture>
</p>

<h1 align="center">crucible</h1>

**Codex turns checked work into learning signal.**

Crucible is a Codex plugin for work that needs proof.

It gives Codex a simple loop:

```text
attempt -> check -> evidence -> promotion
```

Codex can still write. Codex can still repair. Codex can still explain. The difference is that every useful step leaves a trail a human can inspect.

## The Product

A coding agent can finish a task and still leave you with a question:

```text
Should this become something we teach from?
```

Crucible makes that question answerable.

It keeps the task, the attempt, the check, the output, the reward, and the repair together. A failed attempt is not noise. It is the shape of the lesson.

```text
repo -> task -> attempt -> check -> evidence -> learning row
```

The row can later feed whatever training path the researcher cares about. The README does not need to sell the acronym. The value is that the row has proof attached.

## The Rule

```text
No reward without a verifier.
```

A verifier is an executable check that can say what happened. In the current harness, it is just a command in `verifier.yaml`.

The check stays close to the project. Crucible does not hide reward logic in the plugin cache. It copies the task repo into a run workspace, executes the verifier there, and records what happened.

## The Compression

Without a harness, the human carries the whole run in their head.

```text
read task -> inspect attempt -> run check -> read logs -> judge failure -> write repair -> decide what stays
```

With Crucible, the repeatable work becomes an evidence trail.

```text
work held by the human

before Crucible  |████████████████████████████████████████| everything
after Crucible   |████████                                | promote or reject
                  capture, observe, verify, and package move into the harness
```

The loop gets faster because the slow part gets smaller.

## The Operator Split

```text
Codex proposes.
Crucible checks.
The human promotes.
```

Codex may draft the task, verifier, patch, or repair. Crucible runs the check and records the result. The human keeps the gate where judgment matters.

That is the useful boundary: Codex can help create the evidence, but it should not quietly approve its own lesson.

## Why It Feels Easier

Crucible meets Codex where it already works.

Install the plugin:

```bash
codex plugin marketplace add dunkeln/crucible
```

Then ask Codex for a checked task, a verifier-backed repair, or a learning row. The plugin points Codex at the harness instead of making it invent the same scaffold every time.

## What Works Today

Run the demo task:

```bash
./crucible run-task harness/examples/basic-python --promote
```

That command copies the example repo, applies the attempt, runs the verifier, writes the run evidence, and promotes the passing row.

Evidence lands here:

```text
.crucible/projects/<project>/runs/<run_id>/
```

Useful commands:

```bash
./crucible operator-brief researcher --task-dir harness/examples/basic-python
./crucible operator-brief operator --run-dir .crucible/projects/<project>/runs/<run_id>
./crucible scaffold math-rlvr --package crucible_demos
```

If the copied project has `uv.lock`, Python verifiers run in that project environment:

```text
uv run --project . python check.py
```

## Plugin Shape

Crucible ships as a Codex plugin:

```text
.codex-plugin/plugin.json
.codex-plugin/skills/crucible/SKILL.md
harness/
knowledge/
```

The skill tells Codex how to behave: inspect first, choose the seam, use the harness, and report evidence.

The compact doctrine layer lives in [knowledge/](knowledge/). It gives Codex memory without making the memory the runtime.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before changing the repo.

The short rule:

```text
pick one seam, prove it with evidence, and stop
```

Small first. Objective always. Promotion only when the evidence earns it.
