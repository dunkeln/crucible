from __future__ import annotations

import re
import shutil
from pathlib import Path

import yaml

from harness.contracts import path_text
from harness.packs import write_pack


def recipe_pack(source_dirs: tuple[Path, ...], output_root: Path, pack_path: Path, verifier_command: str = "python check.py", force: bool = False) -> dict[str, object]:
    task_dirs = []
    for source_dir in source_dirs:
        task_dir = output_root / slug(source_dir.name)
        if task_dir.exists():
            if not force:
                raise ValueError(f"refusing to overwrite existing task: {task_dir}")
            shutil.rmtree(task_dir)
        write_task(source_dir, task_dir, verifier_command)
        task_dirs.append(task_dir)
    pack = write_pack(tuple(task_dirs), pack_path)
    return {"tasks_root": path_text(output_root), "pack": path_text(pack_path), **pack}


def write_task(source_dir: Path, task_dir: Path, verifier_command: str) -> None:
    if not source_dir.is_dir():
        raise ValueError(f"missing source task directory: {source_dir}")
    task_dir.mkdir(parents=True)
    shutil.copytree(source_dir, task_dir / "repo", ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))
    readme = source_dir / "README.md"
    task_text = readme.read_text(encoding="utf-8") if readme.exists() else f"# {source_dir.name}\n"
    (task_dir / "task.md").write_text(task_text, encoding="utf-8")
    (task_dir / "verifier.yaml").write_text(yaml.safe_dump({"command": verifier_command, "pass_exit_codes": [0], "timeout_seconds": 30}, sort_keys=False), encoding="utf-8")


def slug(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip().lower()).strip("-._") or "task"
