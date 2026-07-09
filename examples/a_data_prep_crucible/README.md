# Case 2A: Crucible Data Prep Verifier

## Goal Prompt

```text
/goal Build `examples/a_data_prep_crucible` as a standalone uv project using Crucible.

Use the Crucible plugin/harness path to turn a messy CSV-style source into a verifier-backed data-prep task. The task should normalize records, catch at least one schema/data-quality issue, keep the adapter/check code inside the example project, run through Crucible, and write evidence under `.crucible/projects/a-data-prep-crucible/`.

Do not build a service or dashboard. Report:
- files created
- source shape
- verifier command
- reward artifact path
- loop.json path
- total input/output token usage if available
```

## Expected Proof

Crucible keeps source chaos outside the harness by forcing an adapter -> verifier -> reward path.

## Measurement

```text
input_tokens:
output_tokens:
files_created:
source_shape:
verifier_command:
reward_artifact:
loop_json:
```
