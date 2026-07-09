# Contributing

Crucible is a Codex-native harness for turning existing work into verifier-backed learning signal.

The contribution rule: pick one seam, prove it with evidence, and stop.

## Seams

### Harness

Owns the loop:

+ apply or generate an attempt
+ run the verifier
+ capture trace, reward, observation, and loop state
+ isolate project artifacts under `.crucible/projects/<project>/`
+ promote only verifier-passing runs with a teacher repair

Keep UI, broad recipe design, and source-specific normalization out of this seam unless the CLI cannot run without it.

### Plugin

Owns Codex behavior:

+ researcher posture
+ operator posture
+ project inspection before assumptions
+ recipe selection
+ bounded prose choices when intent is missing

Do not put harness logic in the skill. The skill should make Codex use the harness, not become the harness.

### Recipes

Own generated artifact shape:

+ files to create
+ known-good defaults
+ verifier command
+ smoke command
+ skip rules

Recipes are factories. Codex selects them; Crucible writes them.

### Ingress Adapters

Own source normalization:

+ Hugging Face datasets
+ Scale-style exports
+ local CSV, JSONL, Parquet, or DuckDB
+ optional `dlt` ingestion

Adapters absorb source chaos and emit recipe inputs. They must not change reward, verifier, loop, or promotion contracts.

### Demo Surface

Owns explanation and inspection only.

It may show task, attempt, verifier result, reward, loop state, and promoted rows. It must not become the source of truth.

## Before Editing

Write down the seam in your PR or commit message:

```text
primary seam:
secondary seam:
why crossing is needed:
what stays unchanged:
```

If more than one seam changes, the reason should be concrete. "Future flexibility" is not enough.

## Checks

Use the smallest runnable check that proves the changed path.

Common checks:

```bash
python -m compileall -q harness
./crucible run-task harness/examples/basic-python --project smoke --promote
./crucible operator-brief researcher --task-dir harness/examples/basic-python
```

For uv-scoped user projects, verifier commands must run in the copied project environment:

```yaml
command: "uv run --project . python check.py"
```

The harness may rewrite plain `python ...` to `uv run --project . python ...` when `uv.lock` exists. The recorded run artifacts must show the effective command.

## Do Not Grow

+ no services when files work
+ no databases before one row needs them
+ no generic schema before two recipes need the same field
+ no required `dlt`; it is optional ingress
+ no promotion without a passing verifier
+ no Codex-owned promotion gate
+ no new dependency for what stdlib or the current stack already does

## PR Shape

Keep PRs vertical and small:

```text
problem:
why it matters:
what changed:
evidence:
what did not change:
```

Good PRs leave a run artifact, a short explanation, or both.
