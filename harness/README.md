# Crucible harness

The harness turns a task attempt into evidence.

It keeps the loop small:

```text
task -> attempt -> verifier -> reward evidence -> repair -> promotion
```

The important move is not that Codex writes more files. It is that Codex gets a smaller surface to operate on. The harness keeps task shape, verifier commands, run evidence, and promotion boundaries in one place, so follow-up turns can start from the current state instead of rebuilding the room.

## Shape

A task is just a small project plus the check that judges it:

```text
task.md
verifier.yaml
repo/
attempt.patch
teacher.patch
```

`repo/` is the copied project workspace. Put verifier code, reward code, rubrics, and judge code there. Crucible runs the check and records the evidence; it does not hide project logic inside the plugin cache.

Minimum verifier:

```yaml
command: "python check.py"
pass_exit_codes: [0]
timeout_seconds: 30
```

## Run

From the repository root:

```bash
./crucible doctor
./crucible run-task harness/examples/basic-python --promote
```

The run writes an isolated evidence folder:

```text
.crucible/projects/<project>/runs/<run_id>/
  task.md
  verifier.yaml
  workspace/
  trace.txt
  reward.json
  observation.json
  loop.json
  run.json
```

Use `--project <name>` when one Crucible checkout runs tasks for multiple projects.

## Repeat

Once the task set is known, lock it:

```bash
./crucible lock-pack harness/examples/basic-python harness/examples/benchmark-even harness/examples/benchmark-normalize --output harness/examples/benchmark-pack.lock.json
```

Then replay the pack:

```bash
./crucible run-pack harness/examples/benchmark-pack.lock.json --project benchmark --runs-csv .crucible/pack-runs.csv
```

The lock stores the task ids, task paths, verifier commands, timeout rules, and patch availability. That is the cheap path: Codex does not need to rediscover the same shape on every turn.

## Continue

For follow-up turns, ask for the next bounded action:

```bash
./crucible next researcher --pack .crucible/pack.lock.json --project benchmark
./crucible next operator --pack .crucible/pack.lock.json --project benchmark --task basic-python
```

`researcher` reads evidence and names the weak task. `operator` lists the likely edit files, the files to avoid, the exact check command, and the latest failure excerpt.

That is the working-memory surface. It keeps the next Codex turn close to the failing behavior instead of asking the model to reopen the whole artifact trail.

## Inspect

Use summaries before opening raw artifacts:

```bash
./crucible list-runs --project benchmark --limit 5
./crucible summarize-run .crucible/projects/<project>/runs/<run_id>
```

Default output is compact. Use `--json-full` only when debugging needs the complete run record.

## Promote

Promotion requires a passing verifier and `teacher.patch`.

A passing check says the attempt crossed the boundary. The teacher repair says what should be taught. Crucible keeps those as separate facts so a run can be inspected before it becomes a reusable row.

## Generate

If a source already has task folders with `README.md` and a runnable check, generate Crucible contracts around it:

```bash
./crucible recipe-pack tasks/* --output-root .crucible/tasks --pack .crucible/pack.lock.json
```

For deterministic setup, let the harness write the scaffold:

```bash
./crucible scaffold math-rlvr --root ../crucible_demos --package crucible_demos
```

The stable code writes the repeatable files. Codex should spend its tokens on the project-specific edge.

## Operator seam

The harness has two Codex-facing roles:

+ `researcher`: inspect tasks and runs, then ask the better question.
+ `operator`: prepare the smallest patch and run the listed check.

Generate a prompt from current evidence:

```bash
./crucible operator-brief researcher --task-dir harness/examples/basic-python
./crucible operator-brief operator --run-dir .crucible/projects/<project>/runs/<run_id>
```

The rule stays the same across human and Codex operation:

```text
capture first -> observe second -> promote last
```
