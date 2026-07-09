from __future__ import annotations

import json
from pathlib import Path

from harness.contracts import PromotionResult, RewardRecord, utc_now


def promote_run(run_dir: Path | str, dataset_root: Path | str = "data/dataset") -> PromotionResult:
    path = Path(run_dir)
    reward = RewardRecord.model_validate_json((path / "reward.json").read_text(encoding="utf-8"))
    if not reward.passed:
        raise ValueError(f"promotion requires passing verifier: {reward.reason}")
    task = (path / "task.md").read_text(encoding="utf-8")
    verifier = (path / "verifier.yaml").read_text(encoding="utf-8")
    attempt = read_optional(path / "attempt.patch")
    teacher = read_optional(path / "teacher.patch")
    if not teacher:
        raise ValueError("promotion requires teacher.patch")

    dataset_path = Path(dataset_root)
    dataset_path.mkdir(parents=True, exist_ok=True)
    sft_row = {
        "messages": [
            {"role": "user", "content": task},
            {"role": "assistant", "content": teacher},
        ],
        "metadata": {
            "run_id": reward.run_id,
            "task_id": reward.task_id,
            "verifier": verifier,
            "source": "crucible",
        },
    }
    rlvr_row = {
        "task_id": reward.task_id,
        "run_id": reward.run_id,
        "task": task,
        "attempt_patch": attempt,
        "teacher_patch": teacher,
        "verifier": verifier,
        "reward": reward.reward,
        "passed": reward.passed,
        "reason": reward.reason,
        "trace_path": (path / "trace.txt").as_posix(),
    }

    run_sft = path / "sft.jsonl"
    run_rlvr = path / "rlvr.jsonl"
    write_jsonl(run_sft, sft_row)
    write_jsonl(run_rlvr, rlvr_row)
    append_jsonl(dataset_path / "sft.jsonl", sft_row)
    append_jsonl(dataset_path / "rlvr.jsonl", rlvr_row)
    return PromotionResult(
        run_id=reward.run_id,
        dataset_root=dataset_path.as_posix(),
        sft_path=run_sft.as_posix(),
        rlvr_path=run_rlvr.as_posix(),
        promoted_at=utc_now(),
    )


def read_optional(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_jsonl(path: Path, row: dict) -> None:
    path.write_text(json.dumps(row, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, sort_keys=True) + "\n")
