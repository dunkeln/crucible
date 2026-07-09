# Normalize messy ingress records

The repo receives user-source records with inconsistent key casing, whitespace, and aliases.

Normalize each record into stable keys:

+ `record_id` and `id` become `id`
+ `question` and `prompt` become `prompt`
+ `gold` and `answer` become `answer`
+ unknown fields stay present under cleaned snake-case keys
+ string values are trimmed

Make the verifier pass without changing the verifier.
