# Crucible A/B Proof Plan

This folder defines six goal prompts for measuring Codex with and without Crucible.

Each case is its own standalone uv project. The `a_*_crucible` cases use the Crucible plugin and harness. The `b_*_raw` cases ask Codex to build the same shape directly, without Crucible.

The proof is not whether both sides can finish. The proof is how much Codex has to invent, how much evidence survives, and how much token output is spent to reach a verifier-backed result.

## Measurement

For every case, record:

+ total input tokens
+ total output tokens
+ files created
+ verifier or check command
+ evidence path
+ reward representation
+ whether the result is reusable as an SFT/RLVR row

## Cases

| Case | Path | Question |
| --- | --- | --- |
| 1A | `a_math_rlvr_crucible` | Can Crucible turn exact-answer math into a verifier-backed RLVR row? |
| 1B | `b_math_rlvr_raw` | How much does raw Codex invent for the same math scaffold? |
| 2A | `a_data_prep_crucible` | Can Crucible bound messy data prep behind a verifier? |
| 2B | `b_data_prep_raw` | How much does raw Codex invent for the same data-prep task? |
| 3A | `a_judge_boundary_crucible` | Can Crucible contain an LLM-judge-shaped verifier as project-local code? |
| 3B | `b_judge_boundary_raw` | How much does raw Codex invent for the same judge boundary? |

## Report Template

```text
case:
status:
input_tokens:
output_tokens:
files_created:
verifier_or_check:
evidence:
reward_shape:
notes:
```
