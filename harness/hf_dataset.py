from __future__ import annotations

import json
import shutil
from pathlib import Path

from harness.contracts import path_text, utc_now
from harness.runner import read_verifier


REQUIRED_TASK_FILES = ("task.md", "verifier.yaml", "attempt.patch", "trace.txt", "reward.json", "teacher.patch")


def export_hf_dataset(source_root: Path | str, output_root: Path | str, validation_size: int = 1) -> dict[str, object]:
    source = Path(source_root)
    destination = Path(output_root)
    task_dirs = discover_task_dirs(source)
    if not task_dirs:
        raise ValueError(f"no runtime task artifacts found under {source}")

    destination.mkdir(parents=True, exist_ok=True)
    data_dir = destination / "data"
    examples_dir = destination / "examples"
    data_dir.mkdir(parents=True, exist_ok=True)
    examples_dir.mkdir(parents=True, exist_ok=True)

    rows = [build_row(task_dir, source.name) for task_dir in task_dirs]
    train_rows, validation_rows = split_rows(rows, validation_size)

    for task_dir, row in zip(task_dirs, rows):
        copy_example(task_dir, examples_dir / str(row["id"]))

    write_jsonl(data_dir / "train.jsonl", train_rows)
    write_jsonl(data_dir / "validation.jsonl", validation_rows)
    write_dataset_card(destination / "README.md", source, len(rows), len(train_rows), len(validation_rows))

    return {
        "source_root": path_text(source),
        "output_root": path_text(destination),
        "train_path": path_text(data_dir / "train.jsonl"),
        "validation_path": path_text(data_dir / "validation.jsonl"),
        "train_rows": len(train_rows),
        "validation_rows": len(validation_rows),
        "generated_at": utc_now().isoformat(),
    }


def discover_task_dirs(source: Path) -> list[Path]:
    if is_task_artifact_dir(source):
        return [source]
    if not source.exists():
        return []
    return sorted(path for path in source.iterdir() if path.is_dir() and is_task_artifact_dir(path))


def is_task_artifact_dir(path: Path) -> bool:
    return all((path / filename).exists() for filename in REQUIRED_TASK_FILES)


def build_row(task_dir: Path, repo_name: str) -> dict[str, object]:
    reward = json.loads((task_dir / "reward.json").read_text(encoding="utf-8"))
    task_text = (task_dir / "task.md").read_text(encoding="utf-8")
    verifier = read_verifier(task_dir / "verifier.yaml")
    attempt_patch = (task_dir / "attempt.patch").read_text(encoding="utf-8")
    trace_text = (task_dir / "trace.txt").read_text(encoding="utf-8")
    teacher_patch = (task_dir / "teacher.patch").read_text(encoding="utf-8")
    task_id = str(reward.get("task_id") or task_dir.name)
    return {
        "id": task_id,
        "repo": repo_name,
        "task": task_text,
        "verifier_command": verifier.command,
        "attempt_patch": attempt_patch,
        "trace": trace_text,
        "exit_code": int(reward.get("exit_code", 1)),
        "passed": bool(reward.get("passed", False)),
        "reward": int(reward.get("reward", 0)),
        "failure_reason": str(reward.get("reason", "verifier failed")),
        "teacher_patch": teacher_patch,
        "sft_messages": [
            {"role": "user", "content": task_text},
            {"role": "assistant", "content": teacher_patch},
        ],
        "rlvr": {
            "prompt": task_text,
            "completion": teacher_patch,
            "reward": int(reward.get("reward", 0)),
            "verifier": verifier.command,
        },
    }


def split_rows(rows: list[dict[str, object]], validation_size: int) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    if not rows:
        return [], []
    clamped_validation = max(0, min(validation_size, len(rows)))
    if clamped_validation == 0:
        return rows, []
    if clamped_validation == len(rows):
        return rows[:-1], rows[-1:]
    return rows[:-clamped_validation], rows[-clamped_validation:]


def copy_example(task_dir: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True, exist_ok=True)
    for filename in REQUIRED_TASK_FILES:
        shutil.copy2(task_dir / filename, destination / filename)
    source_repo = task_dir / "repo"
    if not source_repo.exists():
        source_repo = task_dir / "workspace"
    if source_repo.exists():
        shutil.copytree(source_repo, destination / "repo", ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def write_dataset_card(path: Path, source_root: Path, total_rows: int, train_rows: int, validation_rows: int) -> None:
    text = f"""# Crucible Runtime Dataset

This dataset export is generated from runtime Crucible task artifacts.

Source root: `{path_text(source_root)}`
Generated at: `{utc_now().isoformat()}`

## Splits

+ train: {train_rows}
+ validation: {validation_rows}
+ total: {total_rows}

## Row shape

Each JSONL row contains:

+ task prompt
+ verifier command
+ failed attempt patch
+ verifier trace
+ reward evidence
+ teacher repair patch
+ SFT messages
+ RLVR prompt/completion/reward/verifier fields
"""
    path.write_text(text, encoding="utf-8")
