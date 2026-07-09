from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field


class HarnessModel(BaseModel):
    model_config = ConfigDict(frozen=True)


class OperatorMode(StrEnum):
    HUMAN = "human"
    CODEX = "codex"


class ApprovalMode(StrEnum):
    MANUAL = "manual"
    PROPOSED = "proposed"
    AUTO_SAFE = "auto_safe"


class VerifierSpec(HarnessModel):
    command: str
    pass_exit_codes: list[int] = Field(default_factory=lambda: [0])
    timeout_seconds: int = 30


class CommandResult(HarnessModel):
    command: str
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    started_at: datetime
    finished_at: datetime


class RewardRecord(HarnessModel):
    run_id: str
    task_id: str
    passed: bool
    reward: int
    reason: str
    verifier_command: str
    exit_code: int
    failure_class: str | None
    operator: OperatorMode
    approval_mode: ApprovalMode
    observed_at: datetime


class RunObservation(HarnessModel):
    observation_id: str
    run_id: str
    task_id: str
    pattern_id: str
    verifier_command: str
    passed: bool
    reward: int
    failure_class: str | None
    observed_at: datetime
    operator: OperatorMode
    approval_mode: ApprovalMode


class LoopAttempt(HarnessModel):
    run_id: str
    passed: bool
    reward: int
    failure_class: str | None
    reason: str


class LoopState(HarnessModel):
    loop_id: str
    goal: str
    recipe: str
    attempts: list[LoopAttempt]
    last_failure: str | None
    next_action: str
    iteration_cap: int
    stop_reason: str
    updated_at: datetime


class RunRecord(HarnessModel):
    run_id: str
    task_id: str
    run_dir: str
    workspace_dir: str
    operator: OperatorMode
    approval_mode: ApprovalMode
    verifier: VerifierSpec
    reward: RewardRecord
    loop: LoopState
    artifacts: dict[str, str]
    raw_artifacts: dict[str, str]
    created_at: datetime


class PromotionResult(HarnessModel):
    run_id: str
    dataset_root: str
    sft_path: str
    rlvr_path: str
    promoted_at: datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def path_text(path: Path) -> str:
    return path.as_posix()
