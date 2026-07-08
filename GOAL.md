# Goal - Build the Crucible Harness

Build an end-to-end `harness/` directory for Crucible.

Crucible uses a simple data-harness pattern for code-model training data:

```text
capture raw evidence -> observe behavior -> promote durable rows

task repo -> attempt trace -> verifier observation -> reward -> SFT/RLVR row
```

Do not invent a platform. Build the small harness pipeline described below.

## Working Rules

+ Ponytail mode: smallest complete vertical slice, no speculative platform.
+ Filesystem first. No database until JSONL/files become painful.
+ Use boring harness shapes: CLI group, frozen Pydantic contracts, raw artifact loader, append-only manifests, observation records, promotion boundary.
+ Import needed project dependencies instead of hand-rolling parsers or CLIs. `click`, `pydantic`, and `pyyaml` are fine for this slice.
+ Keep this contained in `harness/`. Do not build the demo surface or HF corpus here.
+ The agent loop can come later. This task is the harness contract and runnable pipeline.

## Target Loop

```text
task_dir
  -> copy repo into isolated workspace
  -> apply attempt.patch
  -> run verifier.yaml command
  -> capture stdout/stderr/exit code
  -> write trace.txt
  -> write reward.json
  -> write observation.json
  -> append evidence indexes
  -> optionally promote teacher.patch into SFT/RLVR JSONL
```

## Task Directory Contract

Minimum task:

```text
task.md
verifier.yaml
repo/
attempt.patch
teacher.patch
```

Minimum `verifier.yaml`:

```yaml
command: "python check.py"
pass_exit_codes: [0]
timeout_seconds: 30
```

`attempt.patch` is the student attempt. `teacher.patch` is required only for promotion.

## Harness Files

Build or preserve this shape:

```text
harness/
  AGENTS.md
  README.md
  __init__.py
  contracts.py
  load.py
  observations.py
  runner.py
  promote.py
  main.py
  examples/
    basic-python/
      task.md
      verifier.yaml
      attempt.patch
      teacher.patch
      repo/
```

Use these module responsibilities:

+ `main.py` -> Click CLI entrypoint.
+ `contracts.py` -> frozen Pydantic models and shared enums.
+ `load.py` -> raw lake copy and manifest append.
+ `observations.py` -> verifier pattern IDs and append-only observations.
+ `runner.py` -> isolated workspace, patch apply, verifier execution, trace/reward writing.
+ `promote.py` -> promotion boundary that exports dataset rows.

## CLI Contract

The main smoke command must work:

```bash
uv run python -m harness.main run-task harness/examples/basic-python --promote
```

Expected behavior:

+ creates a new run under `data/runs/<run_id>/`
+ copies task files into the run directory
+ copies `repo/` into `workspace/`
+ applies `attempt.patch`
+ runs the verifier command from `verifier.yaml`
+ writes reward and observation files
+ copies raw evidence into `data/lake/`
+ appends manifest/reward/observation JSONL indexes
+ writes `sft.jsonl` and `rlvr.jsonl` when `--promote` is used and `teacher.patch` exists

Also support:

```bash
uv run python -m harness.main promote-run data/runs/<run_id>
```

## Output Contract

A completed run should look like:

```text
data/runs/<run_id>/
  task.md
  verifier.yaml
  attempt.patch
  teacher.patch
  workspace/
  trace.txt
  reward.json
  observation.json
  run.json
  sft.jsonl
  rlvr.jsonl
```

Append-only indexes:

```text
data/manifest.jsonl
data/rewards.jsonl
data/observations.jsonl
```

Generated `data/` must stay gitignored.

## Reward Contract

Keep reward binary for the first slice:

```json
{
  "passed": false,
  "reward": 0,
  "reason": "verifier exited 1",
  "verifier_command": "python check.py",
  "exit_code": 1
}
```

No reward shaping yet. Add it only after the binary loop is proven.

## Promotion Contract

Promotion means converting one completed run into inspectable training rows:

+ SFT row: task prompt -> teacher patch.
+ RLVR row: task, attempt patch, verifier, reward, trace path, teacher patch.

Promotion must fail clearly if `teacher.patch` is missing.

## Example Task

Create one tiny realistic Python task under `harness/examples/basic-python/`.

It should prove the whole loop without external services:

+ a small repo file
+ a verifier script or command
+ a bad attempt patch
+ a teacher patch

The example should be boring and deterministic.

## Completion Evidence

Before calling this done, verify:

+ `uv run python -m harness.main run-task harness/examples/basic-python --promote` exits 0.
+ the command prints JSON with run and promotion details.
+ the run directory contains `trace.txt`, `reward.json`, `observation.json`, `run.json`, `sft.jsonl`, and `rlvr.jsonl`.
+ `data/manifest.jsonl`, `data/rewards.jsonl`, and `data/observations.jsonl` are created.
+ generated `data/` remains ignored by git.
+ `README.md` documents the harness command.

## Non-Goals

+ No web UI.
+ No HF dataset corpus implementation.
+ No model orchestration.
+ No Agents SDK integration.
+ No database.
+ No reward shaping.
+ No broad benchmark generation.

Build the boring harness first. The demo and corpus can consume it after the contract exists.
