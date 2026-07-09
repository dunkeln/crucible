# Crucible harness

The harness is the backend loop for turning repository attempts into reward signal.

It follows a simple data-harness pattern:

```text
capture raw evidence -> observe behavior -> promote only durable value
```

Crucible's version:

```text
task repo -> attempt patch -> verifier run -> reward record -> curated learning rows
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

`command` runs inside the copied `repo/` workspace. Keep `check.py`, reward functions, rubrics, and judge code in that project workspace; Crucible records the result, it does not host the reward code.

## Run it

From the repository root:

```bash
./crucible doctor
./crucible run-task harness/examples/basic-python --promote
```

`doctor` validates plugin shape and prints the next cheap harness commands.

The default output is a compact evidence summary. Add `--json-full` when debugging needs the complete run record.

That creates:

```text
.crucible/projects/<project>/runs/<run_id>/
  task.md
  verifier.yaml
  attempt.patch
  teacher.patch
  workspace/
  trace.txt
  reward.json
  observation.json
  loop.json
  run.json
  sft.jsonl
  rlvr.jsonl
```

Raw artifacts also get copied into `.crucible/projects/<project>/lake/`, with project-local manifest, reward, and observation indexes.

Use `--project <name>` when one Crucible checkout runs tasks for multiple projects.

## Locked packs

When the source already has task folders with `README.md` and a runnable check, generate the Crucible contracts:

```bash
./crucible recipe-pack tasks/* --output-root .crucible/tasks --pack .crucible/pack.lock.json
```

When a task set is known, freeze it once:

```bash
./crucible lock-pack harness/examples/basic-python harness/examples/benchmark-even harness/examples/benchmark-normalize --output harness/examples/benchmark-pack.lock.json
```

Replay it without rediscovering task paths or verifier commands:

```bash
./crucible run-pack harness/examples/benchmark-pack.lock.json --project benchmark --runs-csv .crucible/pack-runs.csv
```

The lockfile stores task ids, task dirs, verifier commands, timeout rules, and whether attempt/teacher patches exist. It is the cheap path for repeated benchmark and recipe runs.

`run-pack` prints only task, pass/fail, reward, run path, and timing by default. Add `--json-full` when debugging needs the complete run records.

Summarize one existing run without opening every artifact:

```bash
./crucible list-runs --project benchmark --limit 5
./crucible summarize-run .crucible/projects/<project>/runs/<run_id>
```

## Promotion boundary

Promotion requires `teacher.patch`. A passing verifier is evidence, not enough by itself; the promoted row needs the corrected solution that should train the student model.

## Codex operators

The harness has hardcoded Codex operator roles:

+ `researcher` inspects tasks/runs and proposes research questions without writes.
+ `operator` drafts harness artifacts on behalf of the human, but does not own promotion.

Generate an operator prompt from current evidence:

```bash
./crucible operator-brief researcher --task-dir harness/examples/basic-python
./crucible operator-brief operator --run-dir .crucible/projects/<project>/runs/<run_id>
```

The Codex SDK integration should consume this brief later. Keep the verifier, reward, filesystem contract, and promotion gate in Crucible.

For Codex-executed attempts:

```bash
./crucible run-codex-task harness/examples/basic-python --approval-mode auto_safe
```

This also prints compact evidence by default. Add `--json-full` when the SDK response or full run record matters.

For deterministic project setup, let Crucible write the scaffold instead of asking Codex to hand-author files:

```bash
./crucible scaffold math-rlvr --root ../crucible_demos --package crucible_demos
```
