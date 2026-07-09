# Case 1A: Crucible Math RLVR

## Goal Prompt

```text
/goal Build `examples/a_math_rlvr_crucible` as a standalone uv project using Crucible.

Use the Crucible plugin/harness path. Codex should select a deterministic recipe, generate the smallest exact-answer math RLVR scaffold, keep verifier/reward code inside the example project, run the verifier through Crucible, and produce the run artifacts under `.crucible/projects/a-math-rlvr-crucible/`.

Do not hand-author unnecessary files. Report:
- files created
- verifier command
- reward artifact path
- loop.json path
- total input/output token usage if available
```

## Expected Proof

Codex acts as planner/operator. Crucible owns the repeatable recipe, verifier run, reward capture, and loop evidence.

## Measurement

```text
input_tokens:
output_tokens:
files_created:
verifier_command:
reward_artifact:
loop_json:
```
