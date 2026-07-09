from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from harness.contracts import HarnessModel


class CodexOperatorRole(StrEnum):
    RESEARCHER = "researcher"
    OPERATOR = "operator"


class CodexOperator(HarnessModel):
    role: CodexOperatorRole
    name: str
    approval_policy: str
    sandbox: str
    can_write: bool
    can_promote: bool
    instructions: str


class OperatorBrief(HarnessModel):
    operator: CodexOperator
    prompt: str
    task_dir: str | None = None
    run_dir: str | None = None


OPERATORS: dict[CodexOperatorRole, CodexOperator] = {
    CodexOperatorRole.RESEARCHER: CodexOperator(
        role=CodexOperatorRole.RESEARCHER,
        name="Crucible Researcher",
        approval_policy="on-request",
        sandbox="read-only",
        can_write=False,
        can_promote=False,
        instructions=(
            "You are the Crucible researcher. You do not build. You read task and run evidence, "
            "find bounded verifier-backed questions, name failure modes, and leave promotion untouched."
        ),
    ),
    CodexOperatorRole.OPERATOR: CodexOperator(
        role=CodexOperatorRole.OPERATOR,
        name="Crucible Operator",
        approval_policy="on-request",
        sandbox="workspace-write",
        can_write=True,
        can_promote=False,
        instructions=(
            "Work on behalf of the human operator inside the harness seam. Draft patches, verifier commands, "
            "reward records, and teacher repairs. Do not promote dataset rows without human approval."
        ),
    ),
}


def operator_brief(
    role: CodexOperatorRole,
    task_dir: Path | str | None = None,
    run_dir: Path | str | None = None,
) -> OperatorBrief:
    operator = OPERATORS[role]
    task_path = Path(task_dir) if task_dir else None
    run_path = Path(run_dir) if run_dir else None
    prompt = "\n\n".join(
        part
        for part in [
            operator.instructions,
            "Crucible rule: no reward without a verifier.",
            task_context(task_path) if task_path else "",
            run_context(run_path) if run_path else "",
            "Return concrete next actions tied to task, verifier, trace, reward, repair, or export artifacts.",
        ]
        if part
    )
    return OperatorBrief(
        operator=operator,
        prompt=prompt,
        task_dir=task_path.as_posix() if task_path else None,
        run_dir=run_path.as_posix() if run_path else None,
    )


def task_context(task_dir: Path) -> str:
    task = read_optional(task_dir / "task.md")
    verifier = read_optional(task_dir / "verifier.yaml")
    return "\n".join(
        [
            f"Task directory: {task_dir.as_posix()}",
            "task.md:",
            task,
            "verifier.yaml:",
            verifier,
        ]
    )


def run_context(run_dir: Path) -> str:
    return "\n".join(
        [
            f"Run directory: {run_dir.as_posix()}",
            "reward.json:",
            read_optional(run_dir / "reward.json"),
            "trace.txt:",
            read_optional(run_dir / "trace.txt"),
        ]
    )


def read_optional(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""
