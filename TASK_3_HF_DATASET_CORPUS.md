# Task 3 - HF Dataset Corpus

## Goal

Build the Crucible task/verifier corpus as a Hugging Face-compatible dataset export.

This is the training-signal surface. The harness should be able to run these tasks, and the demo should be able to display or export the resulting rows.

Dataset export content must be sourced from runtime Crucible artifacts provided by the product flow. Do not hardcode demo dataset rows in repository files.

## Owns

Task 3 owns:

+ example tasks
+ verifier definitions
+ expected failed attempts
+ teacher repairs
+ reward examples
+ HF-ready JSONL dataset rows
+ dataset card

Task 3 does not own:

+ harness orchestration
+ UI/demo behavior
+ agent execution
+ database/storage infrastructure

## Required file shape

```text
datasets/crucible-demo/
  README.md
  data/
    train.jsonl
    validation.jsonl
  examples/
    task-001/
      task.md
      verifier.yaml
      attempt.patch
      trace.txt
      reward.json
      teacher.patch
```

## 2-hour win

Ship:

+ 3 tiny realistic coding tasks
+ each task has `task.md`
+ each task has `verifier.yaml`
+ each task has one bad `attempt.patch`
+ each task has one `teacher.patch`
+ each task has one `reward.json`
+ `data/train.jsonl` exists
+ `data/validation.jsonl` exists
+ `README.md` explains the dataset

## Dataset row contract

Each JSONL row should contain:

```json
{
  "id": "task-001",
  "repo": "demo-python",
  "task": "Fix divide-by-zero behavior",
  "verifier_command": "python -m pytest",
  "attempt_patch": "...",
  "trace": "...",
  "exit_code": 1,
  "passed": false,
  "reward": 0,
  "failure_reason": "Verifier failed because divide_by_zero still raises.",
  "teacher_patch": "...",
  "sft_messages": [],
  "rlvr": {
    "prompt": "...",
    "completion": "...",
    "reward": 0,
    "verifier": "python -m pytest"
  }
}
```

## Done criteria

This task is done when another teammate can answer:

+ What task was attempted?
+ What verifier checks it?
+ What did the bad attempt do?
+ Why did it fail?
+ What reward did it receive?
+ What is the teacher repair?
+ Can this row be loaded as dataset JSONL?

## Non-goals

+ Do not publish to Hugging Face yet.
+ Do not build a large benchmark.
+ Do not invent a complex schema.
+ Do not add a database.

Start with files. Add machinery only when the files become painful.

## Runtime export command

```bash
uv run python -m harness.main export-hf-dataset <runtime_artifact_root> --output-root datasets/crucible-demo
```

`<runtime_artifact_root>` may be one task artifact directory or a parent directory containing multiple task artifact directories.
