# Crucible - working philosophy

Read [README.md](README.md) for the project idea. Read [CONTRIBUTIONS.md](CONTRIBUTIONS.md) before editing so you pick the right seam early. This file is how to work inside it.

## Philosophy

+ Reward evidence, not vibes. A model earns reward by producing work that survives verification.
+ Define the verifier before judging the solution. If the check is unclear, the task is not ready.
+ Keep tasks bounded. Prefer one small repository behavior with a pass/fail signal over a broad improvement story.
+ Preserve roles. Never blur the student attempt, verifier outcome, reward signal, teacher repair, and curated dataset row.
+ Do not perfect the slice. Reason the smallest vertical path end to end, then implement only that.
+ Work in Ponytail mode by default: question whether the work needs to exist, reuse what is already here, prefer stdlib/native features, avoid new dependencies, and ship the shortest diff that actually fixes the real path.

When uncertain, ask: `What would make this objectively verifiable?`

## Ponytail discipline

+ Read the relevant flow first. Small changes in the wrong place are not minimal.
+ Stop at the first rung that holds: skip speculative work, reuse local code, use stdlib/native features, use installed deps, then write the minimum code.
+ Fix root cause once where callers route through it. Do not patch only the named symptom if sibling paths stay broken.
+ No unrequested abstractions, factories, interfaces, config, or scaffolding for later.
+ Mark deliberate shortcuts with a `ponytail:` comment when the ceiling matters.
+ Non-trivial logic needs one runnable check when tests are approved; otherwise report the skipped check clearly.

## While creating tasks

+ Capture first, observe second, promote last.
+ Raw attempts, patches, logs, and verifier output are source of truth.
+ Promotion is the serial gate: only reusable task/verifier/reward patterns become dataset rows.
+ Do not create extra schema, metadata, or folders until one training row needs them.
+ Keep verifier logic objective. If a human has to infer whether it passed, the verifier is not done.

## While issue debugging

Before proposing a debugging change, inspect the full relevant execution path, not necessarily the entire repository.

Relevant execution path means:
+ The entrypoint where the failing behavior is triggered.
+ The modules directly involved in the failing flow.
+ The data contracts, schemas, API boundaries, persistence layer, or external calls touched by that flow.
+ Existing tests or fixtures that describe intended behavior.
+ Nearby analogous flows when they clarify architecture or naming.

Use this RCA pattern:
`why this fails? -> why does this happen? -> why is it possible? -> what contributes to the issue -> what can I change minimally to fix all the whys?`

Before change, think if changing X breaks anything downstream. Use `/azimuth` when the risk is not obvious.

## Code writing practices

+ Do not write unit tests on the same turn as implementation. Tests should be built after approval and when runtime execution failure is reflected.
+ Prevent contract or typed schema sprawling because of naming convention mis-maps.
+ Prefer deletion and reuse over new helpers.
+ Scope small and say why. If unclear, ask for clarification.

## Commits

One commit per issue. Message format: what the problem is, why it matters, what changed, what was not changed.
