# Contributions

Crucible has three early seams. Pick one before editing.

The Codex plugin is the package wrapper over these seams, not a fourth seam.

## 1. Agent harness

Owns running the loop.

+ applies or simulates a model attempt
+ runs the verifier
+ captures traces, logs, patches, and command output
+ writes reward records
+ owns the human/Codex operator switch

Do not build UI here. Do not invent corpus format here unless the harness cannot run without it.

Operator modes belong here:

```text
operator: human | codex
approval_mode: manual | proposed | auto_safe
```

The Codex operator may draft artifacts and request tool actions. The human operator owns approval for seam crossings and promotion.

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

Plugin-facing changes belong in `.codex-plugin/` and `skills/` only when they make the existing harness easier for Codex to operate.
