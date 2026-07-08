# Crucible harness

The harness is the backend loop for turning repository attempts into reward signal.

It follows the Procdork harness pattern:

```text
capture raw evidence -> observe behavior -> promote only durable value
```

Crucible's version:

```text
task repo -> attempt patch -> verifier run -> reward record -> curated SFT/RLVR rows
```

## Contract

A task directory contains:

```text
task.md
verifier.yaml
repo/
attempt.patch      # optional, used by the demo task
teacher.patch      # required for promotion
```

Minimum verifier:

```yaml
command: "python check.py"
pass_exit_codes: [0]
timeout_seconds: 30
```

## Run it

```bash
uv run python -m harness.main run-task harness/examples/basic-python --promote
```

That creates:

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

To export runtime artifacts into Task 3 HF dataset shape:

```bash
uv run python -m harness.main export-hf-dataset data/runs --output-root datasets/crucible-demo
```

This command expects runtime task artifacts with `task.md`, `verifier.yaml`, `attempt.patch`, `trace.txt`, `reward.json`, and `teacher.patch`.

Raw artifacts also get copied into `data/lake/`, with `data/manifest.jsonl`, `data/rewards.jsonl`, and `data/observations.jsonl` as append-only evidence indexes.

## Promotion boundary

Promotion requires `teacher.patch`. A passing verifier is evidence, not enough by itself; the promoted row needs the corrected solution that should train the student model.
