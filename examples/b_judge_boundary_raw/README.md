# Case 3B: Raw Codex Judge Boundary

## Goal Prompt

```text
/goal Build `examples/b_judge_boundary_raw` as a standalone uv project without using Crucible.

Create a minimal judge/rubric example directly. The judge should be deterministic and local, emit bounded JSON, and a check command should decide pass/fail from that output. Keep it runnable with uv. Do not use Crucible, plugin recipes, or `.crucible` artifacts.

Report:
- files created
- judge contract
- check command
- how reward/pass-fail is represented
- what evidence proves it works
- total input/output token usage if available
```

## Expected Proof

Codex owns the judge boundary directly. The run should show whether it keeps the rubric bounded or turns judgment into loose prose.

## Measurement

```text
input_tokens:
output_tokens:
files_created:
judge_contract:
check_command:
reward_shape:
evidence:
```
