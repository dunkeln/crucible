from __future__ import annotations

from hashlib import sha256
import json
import re
from secrets import token_hex
from datetime import UTC, datetime
from pathlib import Path

from harness.contracts import ApprovalMode, OperatorMode, RewardRecord, RunObservation, VerifierSpec, utc_now


def observe_run(
    run_id: str,
    task_id: str,
    verifier: VerifierSpec,
    reward: RewardRecord,
    operator: OperatorMode,
    approval_mode: ApprovalMode,
) -> RunObservation:
    canonical = canonicalize_command(verifier.command)
    pattern = "|".join([canonical, str(reward.passed), reward.failure_class or "passed"])
    return RunObservation(
        observation_id=f"obs_{sha256(f'{run_id}|{pattern}'.encode()).hexdigest()[:12]}",
        run_id=run_id,
        task_id=task_id,
        pattern_id=f"verifier_{sha256(pattern.encode()).hexdigest()[:12]}",
        verifier_command=verifier.command,
        passed=reward.passed,
        reward=reward.reward,
        failure_class=reward.failure_class,
        observed_at=utc_now(),
        operator=operator,
        approval_mode=approval_mode,
    )


def append_observation(observation: RunObservation, path: Path | str = "data/observations.jsonl") -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as observations:
        observations.write(json.dumps(observation.model_dump(mode="json"), sort_keys=True) + "\n")


def new_run_id(prefix: str = "run") -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{prefix}_{timestamp}_{token_hex(4)}"


def canonicalize_command(command: str) -> str:
    # ponytail: regex canonicalizer; use shell parsing if verifier syntax becomes a reward feature.
    text = re.sub(r"\b\d+(?:\.\d+)?\b", "?", command)
    return re.sub(r"\s+", " ", text).strip().lower()


def failure_class(passed: bool, exit_code: int, stderr: str) -> str | None:
    if passed:
        return None
    if exit_code == 124:
        return "timeout"
    if "assert" in stderr.lower():
        return "assertion"
    if "syntaxerror" in stderr.lower():
        return "syntax"
    return "nonzero_exit"
