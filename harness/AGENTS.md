# Crucible harness

This directory owns the agent harness seam:

+ run bounded task attempts
+ capture raw evidence
+ observe verifier outcomes
+ write reward records
+ promote curated rows

Keep demo UI and task corpus ownership outside this seam unless the CLI cannot run without the change.
