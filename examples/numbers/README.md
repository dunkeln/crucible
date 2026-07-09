# Numbers

Measured on July 9, 2026 with two fresh Codex CLI sessions in `/tmp/crucible-numbers-bench-v2`.

Both arms fixed the same follow-up ingress-normalization task and passed the verifier.

+ `without_crucible`: plain task folder, loose prose, manual evidence file.
+ `with_crucible`: locked Crucible pack, failing prior evidence, loose prose, `crucible next` brief.

`fresh_input_tokens = input_tokens - cached_input_tokens`.

`billable_proxy_tokens = fresh_input_tokens + output_tokens`.

The source rows are in [summary.csv](summary.csv).
