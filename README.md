# Crucible

![Crucible logo](assets/logo.png)

**No reward without a verifier.**

Crucible is a Codex-native plugin and RLVR harness for small code models.

It turns real repository work into verifiable training signal. The point is not to make a model sound right. The point is to reward work that survives objective checks.

Ponytail makes coding agents write less code. Crucible makes training agents produce verifiable reward signal.

## The simple story

Generic coding agents optimize for completing a task. Crucible optimizes for producing a clean training row from a task.

```text
repo -> bounded task -> model attempt -> verifier result -> reward -> teacher repair -> SFT/RLVR row
```

The distinction matters. A failed attempt is not waste. It is evidence. The verifier output, patch, logs, and repair explain what the model did, why it failed, and what correction is worth teaching.

## The harness bet

Crucible borrows the shape of a measured harness:

```text
capture first -> observe second -> promote last
```

Raw attempts and traces are kept as evidence. Verifier outcomes become observations. Reward records explain the judgment. Only after the task, verifier, and reward pattern are reusable does anything get promoted into a curated dataset row.

That keeps the serial gate small. We do not design a grand schema before seeing useful failures. We capture the run, learn from the trace, and promote only the part that earns durability.

## What stays raw

Raw evidence should stay close to the run:

+ attempted patch
+ command output
+ verifier logs
+ failure trace
+ reward reason
+ teacher repair note

Do not rewrite raw evidence to fit the first reward story. The raw trace is the source of truth.

## What gets promoted

Promotion is the boundary where noisy run evidence becomes durable training material.

```text
raw attempt -> verifier observation -> reward record -> curated task -> stable verifier -> dataset row
```

A promoted row should let a researcher answer:

+ What was the task?
+ What did the model try?
+ What did the verifier check?
+ What reward was assigned?
+ Why did attempts fail?
+ What was the corrected solution?
+ Can this row be safely used for SFT or RLVR training?

## Operator model

Crucible should support two operators over the same harness contract:

```text
human operator -> chooses task, approves seam crossings, promotes rows
codex operator -> proposes attempts, runs bounded tools, writes draft artifacts
```

The switch is not a different architecture. It is a mode bit on the same run:

```text
operator: human | codex
approval_mode: manual | proposed | auto_safe
```

Manual mode means the human executes or approves each sensitive step. Proposed mode means the Codex operator can prepare patches, verifier commands, rewards, and teacher repairs, but the human approves writes and promotion. Auto-safe mode is only for replayable, low-risk runs where the verifier and output paths are already fixed.

The Codex operator may work on behalf of the human, but it should not own the promotion gate. Promotion is where human judgment mitigates agent autonomy in critical seams.

For an Agents SDK implementation, keep the SDK agent inside the harness seam. The SDK owns the agent loop, tool calls, approvals, tracing, and run state; Crucible still owns the filesystem contract, verifier contract, reward contract, and promotion decision.

## Codex plugin shape

Crucible ships as a Codex plugin:

```text
.codex-plugin/plugin.json
skills/crucible/SKILL.md
harness/
```

The plugin skill lets a scientist ask Codex to discover verifier-backed tasks, run the harness, inspect failures, curate teacher repairs, and export SFT/RLVR rows without learning a new platform.

The Codex SDK belongs behind the harness operator seam. Use it when Crucible needs a local Codex thread to act as the `research_assistant` or `operator`; keep all writes, verifier runs, reward records, and promotion decisions flowing through the harness contract.

### Install via GitHub marketplace

This repo includes a marketplace file at `.agents/plugins/marketplace.json`, so Codex can load Crucible directly from GitHub:

```bash
codex plugin marketplace add dunkeln/crucible
```

Then open the Codex plugin directory and install `Crucible` from the `Crucible Marketplace` source.

## Scientist workflow

The first useful workflow is:

```bash
crucible init
crucible doctor
crucible task discover --limit 5
crucible rollout --model qwen2.5-coder-1.5b --n 4
crucible verify
crucible export --rlvr
```

The current MVP proves the core slice with:

```bash
./crucible run-task harness/examples/basic-python --promote
./crucible operator-brief research_assistant --task-dir harness/examples/basic-python
```

The first wow moment is not training a model. It is turning a repo into a verifiable SLM training dataset.

## Artifact shape

Use structured files when they help the row stay inspectable:

+ `task.md`
+ `verifier.yaml`
+ `rollout.jsonl`
+ `rewards.jsonl`
+ `trace.txt`
+ `teacher_patch.diff`
+ `sft.jsonl`
+ `rlvr.jsonl`
+ `report.md`

These are artifacts, not a schema mandate. Add the file when the row needs it.

## Harness quickstart

The runnable harness lives in [harness/](harness/).

```bash
./crucible run-task harness/examples/basic-python --promote
```

That command applies the demo attempt in an isolated workspace, runs `verifier.yaml`, writes raw evidence under `.crucible/runs/<run_id>/`, records reward evidence, and promotes one SFT/RLVR row.

## The leverage

Crucible is the loop:

```text
bound the task
define the verifier
run the attempt
score from evidence
repair causally
export the row
```

Small first. Objective always. Promotion only when the evidence earns it.
