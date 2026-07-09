# Curate a failure repair

A previous attempt fixed the visible import error by adding a shim, but the root entrypoint still pointed at a missing `demo_surface` package contract.

Promote evidence that includes:

+ the failing attempt
+ the verifier result for that failed attempt
+ the smallest repair
+ a teacher note explaining the root cause

Make the verifier pass without changing the verifier.
