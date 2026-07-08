---
name: crucible
description: Use when a user wants Codex to create verifier-backed coding tasks, run or inspect Crucible harness attempts, score rewards from objective verifier output, curate teacher repairs, or export SFT/RLVR dataset rows.
---

# Crucible

Project face: `assets/logo.png`.

Crucible turns a code repo into a verifiable training gym for small models.

The rule is: no reward without a verifier.

## Use this workflow

1. Read `README.md`, `AGENTS.md`, `CONTRIBUTIONS.md`, and `harness/README.md`.
2. Identify the seam before editing: harness, demo surface, or task/verifier corpus.
3. Keep the task bounded and verifier-backed.
4. Use the harness CLI for evidence:

```bash
./crucible run-task harness/examples/basic-python --promote
```

5. Inspect the run artifacts before claiming success:

```text
.crucible/runs/<run_id>/trace.txt
.crucible/runs/<run_id>/reward.json
.crucible/runs/<run_id>/observation.json
.crucible/runs/<run_id>/sft.jsonl
.crucible/runs/<run_id>/rlvr.jsonl
```

## Codex operator modes

Use hardcoded operator roles through the harness, not ad hoc prompting:

+ `research_assistant`: inspect tasks, summarize failures, propose reward questions, and avoid writes.
+ `operator`: prepare patches, verifier commands, reward records, and teacher repairs, but leave promotion to human approval.

For operator prompts, run:

```bash
./crucible operator-brief research_assistant --task-dir harness/examples/basic-python
./crucible operator-brief operator --run-dir .crucible/runs/<run_id>
```

## Do not build

+ hosted RL training
+ model hosting
+ annotation ops
+ generic agent marketplace
+ full observability

Build local verifier-backed data generation.
