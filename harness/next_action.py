from __future__ import annotations

from pathlib import Path

from harness.contracts import RunRecord, path_text
from harness.packs import list_runs, read_pack, run_summary


def next_brief(role: str, pack_path: Path, project: str, crucible_root: Path, task: str | None = None, command: str = "crucible") -> dict[str, object]:
    pack = read_pack(pack_path)
    runs = list_runs(crucible_root, project=project, limit=100)
    latest = latest_by_task(runs)
    tasks = pack["tasks"]
    chosen = choose_task(tasks, latest, task)

    if role == "researcher":
        return researcher_brief(pack_path, project, tasks, latest, command)
    return operator_brief(pack_path, project, chosen, latest.get(chosen["id"]), command)


def researcher_brief(pack_path: Path, project: str, tasks: list[dict], latest: dict[str, RunRecord], command: str) -> dict[str, object]:
    return {
        "role": "researcher",
        "project": project,
        "pack": path_text(pack_path),
        "task_count": len(tasks),
        "runs": [compact_task_state(task, latest.get(task["id"])) for task in tasks],
        "read": [
            f"{command} list-runs --project {project} --limit {len(tasks)}",
            f"{command} summarize-run <run_dir>",
        ],
        "answer": "Name the weakest verifier-backed task. Do not edit files.",
    }


def operator_brief(pack_path: Path, project: str, task: dict, run: RunRecord | None, command: str) -> dict[str, object]:
    task_dir = resolve_pack_task_dir(pack_path, str(task["task_dir"]))
    repo_dir = task_dir / "repo"
    candidates = source_candidates(repo_dir)
    return {
        "role": "operator",
        "project": project,
        "task": task["id"],
        "edit": candidates[:1] if len(candidates) == 1 else candidates[:8],
        "task_dir": path_text(task_dir),
        "do_not_edit": [path_text(task_dir / "task.md"), path_text(task_dir / "verifier.yaml"), path_text(pack_path)],
        "check": f"{command} run-pack {path_text(pack_path)} --project {project}",
        "latest_evidence": compact_run(run),
        "success": "The listed check passes. Report compact evidence paths only.",
    }


def compact_task_state(task: dict, run: RunRecord | None) -> dict[str, object]:
    state: dict[str, object] = {"task": task["id"], "task_dir": task["task_dir"]}
    if run:
        state.update(run_summary(run))
    else:
        state["run_dir"] = None
    return state


def compact_run(run: RunRecord | None) -> dict[str, object] | None:
    if not run:
        return None
    return {
        "run_dir": run.run_dir,
        "passed": run.reward.passed,
        "reward": run.reward.reward,
        "reward_json": run.artifacts.get("reward"),
        "observation_json": run.artifacts.get("observation"),
        "trace": path_text(Path(run.run_dir) / "trace.txt"),
    }


def latest_by_task(runs: list[RunRecord]) -> dict[str, RunRecord]:
    latest: dict[str, RunRecord] = {}
    for run in runs:
        latest.setdefault(run.task_id, run)
    return latest


def choose_task(tasks: list[dict], latest: dict[str, RunRecord], task: str | None) -> dict:
    if task:
        for item in tasks:
            if item["id"] == task:
                return item
        raise ValueError(f"task not in pack: {task}")
    for item in tasks:
        run = latest.get(item["id"])
        if run and not run.reward.passed:
            return item
    return tasks[0]


def resolve_pack_task_dir(pack_path: Path, task_dir: str) -> Path:
    path = Path(task_dir)
    if path.is_absolute() or path.exists():
        return path
    for base in (pack_path.parent, pack_path.parent.parent):
        candidate = base / path
        if candidate.exists():
            return candidate
    return path


def source_candidates(repo_dir: Path) -> list[str]:
    if not repo_dir.exists():
        return [path_text(repo_dir)]
    files = []
    for path in sorted(repo_dir.rglob("*")):
        if path.is_dir() or path.name.startswith(".") or "__pycache__" in path.parts:
            continue
        if path.name in {"check.py", "README.md"} or path.suffix in {".pyc", ".lock"}:
            continue
        files.append(path_text(path))
    return files or [path_text(repo_dir)]
