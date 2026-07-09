cause: `main.py` imported `demo_surface.main`, but no `demo_surface` package exists in the repo.

repair: route the root Python entrypoint to the existing `harness.main` CLI, matching the `./crucible` launcher.

lesson: fix stale shared entrypoints at the source; adding import-path shims would hide the symptom while leaving the missing module contract false.
