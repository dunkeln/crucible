# Case 3A: Crucible Judge Boundary

## Goal Prompt

```text
/goal Build `examples/a_judge_boundary_crucible` as a standalone uv project using Crucible.

Use the Crucible plugin/harness path to create a verifier-backed task where deterministic checks are insufficient, so the project contains a tiny local judge/rubric stub. The judge must emit bounded JSON, the verifier must convert that into pass/fail plus reward evidence, and Crucible must record trace, reward, and loop artifacts under `.crucible/projects/a-judge-boundary-crucible/`.

Do not call a real paid model. Stub the judge deterministically. Report:
- files created
- judge contract
- verifier command
- reward artifact path
- loop.json path
- total input/output token usage if available
```

## Expected Proof

Crucible contains judge-shaped reward behind project-local executable code and records the evidence without making the plugin the judge.

## Measurement

```text
input_tokens:
output_tokens:
files_created:
judge_contract:
verifier_command:
reward_artifact:
loop_json:
```
