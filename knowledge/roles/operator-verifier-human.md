---
type: Role Boundary
title: Operator, Verifier, Human
description: Codex can operate inside the harness, but the verifier and human gate decide what survives.
tags: [operator, verifier, human-gate]
---

# Roles

```text
Codex operator = selects recipe, drafts small deltas, checks output
Crucible = deterministic artifact generator and harness
Verifier = truth function
Human = promotion gate
```

The Codex operator may act on behalf of the human, but it does not own promotion.

# Selection

When recipe choice is missing, ask with numbered Markdown options and accept `1`, `2`, `3`, or the recipe name.

