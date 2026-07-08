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

Raw artifacts also get copied into `data/lake/`, with `data/manifest.jsonl`, `data/rewards.jsonl`, and `data/observations.jsonl` as append-only evidence indexes.

## Promotion boundary

Promotion requires `teacher.patch`. A passing verifier is evidence, not enough by itself; the promoted row needs the corrected solution that should train the student model.

## Codex operators

The harness has hardcoded Codex operator roles:

+ `research_assistant` inspects tasks/runs and proposes research questions without writes.
+ `operator` drafts harness artifacts on behalf of the human, but does not own promotion.

Generate an operator prompt from current evidence:

```bash
uv run python -m harness.main operator-brief research_assistant --task-dir harness/examples/basic-python
uv run python -m harness.main operator-brief operator --run-dir data/runs/<run_id>
```

The Codex SDK integration should consume this brief later. Keep the verifier, reward, filesystem contract, and promotion gate in Crucible.

Install the optional SDK dependency only when building that operator loop:

```bash
uv sync --extra codex
```
