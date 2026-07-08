# Contributions

Crucible has three early seams. Pick one before editing.

## 1. Agent harness

Owns running the loop.

+ applies or simulates a model attempt
+ runs the verifier
+ captures traces, logs, patches, and command output
+ writes reward records

Do not build UI here. Do not invent corpus format here unless the harness cannot run without it.

## 2. Demo surface

Owns showing the loop.

+ lists available tasks or runs
+ displays task, attempt, verifier result, reward, and teacher repair
+ exports or links to the curated row

Do not own verifier logic here. Do not make the UI source of truth.

## 3. Task and verifier corpus

Owns the training signal.

+ `task.md`
+ `verifier.yaml`
+ seed attempts or expected failures
+ reward rubric
+ curated `sft.jsonl` and `rlvr.jsonl` examples

Do not build orchestration here. Do not make a new schema until one real row needs it.

## Boundary rule

If a change touches more than one seam, state the seam crossing first:

```text
primary seam:
secondary seam:
why crossing is needed:
what stays unchanged:
```

Default to files over services, hardcoded demo data over databases, and one runnable vertical slice over reusable infrastructure.
