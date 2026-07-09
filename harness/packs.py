from __future__ import annotations

import csv
import json
import time
from pathlib import Path

from harness.contracts import RunRecord, path_text
from harness.runner import read_verifier


RUNS_CSV_FIELDS = [
    "task",
    "arm",
    "loc_changed",
    "input_tokens",
    "cached_input_tokens",
    "output_tokens",
    "wall_seconds",
    "input_price_per_mtok",
    "cached_input_price_per_mtok",
    "output_price_per_mtok",
    "tool_cost_usd",
    "regional_multiplier",
    "passed",
    "evidence_path",
]


def write_pack(task_dirs: tuple[Path, ...], output: Path) -> dict:
    tasks = []
    for task_dir in task_dirs:
        verifier = read_verifier(task_dir / "verifier.yaml")
        tasks.append(
            {
                "id": task_dir.name,
                "task_dir": path_text(relative_path(task_dir)),
                "verifier_command": verifier.command,
                "pass_exit_codes": verifier.pass_exit_codes,
                "timeout_seconds": verifier.timeout_seconds,
                "attempt_patch": (task_dir / "attempt.patch").exists(),
                "teacher_patch": (task_dir / "teacher.patch").exists(),
            }
        )

    pack = {
        "version": 1,
        "tasks": tasks,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(pack, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return pack


def read_pack(path: Path) -> dict:
    pack = json.loads(path.read_text(encoding="utf-8"))
    if pack.get("version") != 1:
        raise ValueError(f"unsupported pack version: {pack.get('version')}")
    if not isinstance(pack.get("tasks"), list) or not pack["tasks"]:
        raise ValueError("pack has no tasks")
    return pack


def timed_run(call) -> tuple[RunRecord, float]:
    started = time.perf_counter()
    record = call()
    return record, time.perf_counter() - started


def benchmark_row(task_id: str, arm: str, run_dir: Path, wall_seconds: float) -> dict[str, object]:
    return {
        "task": task_id,
        "arm": arm,
        "loc_changed": patch_loc(run_dir / "attempt.patch"),
        "input_tokens": "NA",
        "cached_input_tokens": "NA",
        "output_tokens": "NA",
        "wall_seconds": f"{wall_seconds:.2f}",
        "input_price_per_mtok": "NA",
        "cached_input_price_per_mtok": "NA",
        "output_price_per_mtok": "NA",
        "tool_cost_usd": 0,
        "regional_multiplier": 1,
        "passed": "true" if read_run(run_dir).reward.passed else "false",
        "evidence_path": path_text(run_dir),
    }


def run_summary(record: RunRecord, wall_seconds: str | None = None) -> dict[str, object]:
    summary: dict[str, object] = {
        "task": record.task_id,
        "passed": record.reward.passed,
        "reward": record.reward.reward,
        "reason": record.reward.reason,
        "run_dir": record.run_dir,
    }
    if wall_seconds is not None:
        summary["wall_seconds"] = wall_seconds
    return summary


def read_run(run_dir: Path) -> RunRecord:
    return RunRecord.model_validate_json((run_dir / "run.json").read_text(encoding="utf-8"))


def list_runs(crucible_root: Path, project: str | None = None, limit: int = 10) -> list[RunRecord]:
    projects_root = crucible_root / "projects"
    if project:
        run_jsons = (projects_root / project / "runs").glob("*/run.json")
    else:
        run_jsons = projects_root.glob("*/runs/*/run.json")
    records = [read_run(path.parent) for path in sorted(run_jsons, reverse=True)]
    return records[:limit]


def append_rows(path: Path, rows: list[dict[str, object]]) -> None:
    exists = path.exists() and path.stat().st_size > 0
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=RUNS_CSV_FIELDS)
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def patch_loc(path: Path) -> int:
    if not path.exists():
        return 0
    changed = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(("+++", "---")):
            continue
        if line.startswith(("+", "-")):
            changed += 1
    return changed


def relative_path(path: Path) -> Path:
    if path.resolve().is_absolute() and Path.cwd().resolve() == Path("/"):
        return path.resolve()
    try:
        return path.resolve().relative_to(Path.cwd().resolve())
    except ValueError:
        return path
