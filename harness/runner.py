from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path

import yaml

from harness.contracts import (
    ApprovalMode,
    CommandResult,
    HarnessModel,
    LoopAttempt,
    LoopState,
    OperatorMode,
    RewardRecord,
    RunRecord,
    VerifierSpec,
    path_text,
    utc_now,
)
from harness.load import append_manifest, load_files
from harness.observations import append_observation, failure_class, new_run_id, observe_run


def run_task(
    task_dir: Path | str,
    attempt_patch: Path | str | None = None,
    runs_root: Path | str = "data/runs",
    lake_root: Path | str = "data/lake",
    manifest_jsonl: Path | str = "data/manifest.jsonl",
    rewards_jsonl: Path | str = "data/rewards.jsonl",
    observations_jsonl: Path | str = "data/observations.jsonl",
    operator: OperatorMode = OperatorMode.HUMAN,
    approval_mode: ApprovalMode = ApprovalMode.MANUAL,
) -> RunRecord:
    task_path = Path(task_dir)
    verifier = read_verifier(task_path / "verifier.yaml")
    task_id = task_path.name
    run_id = new_run_id("run")
    run_dir = Path(runs_root) / run_id
    workspace = run_dir / "workspace"
    run_dir.mkdir(parents=True, exist_ok=False)

    copy_required(task_path / "task.md", run_dir / "task.md")
    copy_workspace(task_path / "repo", workspace)

    patch_path = Path(attempt_patch) if attempt_patch else task_path / "attempt.patch"
    run_patch = run_dir / "attempt.patch"
    if patch_path.exists():
        shutil.copy2(patch_path, run_patch)
        patch_result = run_command(["git", "apply", path_text(run_patch.resolve())], workspace)
    else:
        patch_result = None

    teacher_path = task_path / "teacher.patch"
    if teacher_path.exists():
        shutil.copy2(teacher_path, run_dir / "teacher.patch")

    effective_verifier = verifier.model_copy(update={"command": verifier_command(verifier.command, workspace)})
    write_yaml(run_dir / "verifier.yaml", effective_verifier)
    verifier_result = run_shell(effective_verifier.command, workspace, effective_verifier.timeout_seconds) if patch_result_ok(patch_result) else None
    result_for_reward = verifier_result or patch_result
    if result_for_reward is None:
        raise ValueError("no attempt patch found and no verifier result was produced")

    passed = verifier_result is not None and verifier_result.exit_code in verifier.pass_exit_codes
    reward = RewardRecord(
        run_id=run_id,
        task_id=task_id,
        passed=passed,
        reward=1 if passed else 0,
        reason="verifier passed" if passed else failure_reason(patch_result, verifier_result),
        verifier_command=effective_verifier.command,
        exit_code=result_for_reward.exit_code,
        failure_class=failure_class(passed, result_for_reward.exit_code, result_for_reward.stderr),
        operator=operator,
        approval_mode=approval_mode,
        observed_at=utc_now(),
    )
    observation = observe_run(run_id, task_id, effective_verifier, reward, operator, approval_mode)
    loop = loop_state(task_id, reward)

    write_json(run_dir / "reward.json", reward.model_dump(mode="json"))
    write_json(run_dir / "observation.json", observation.model_dump(mode="json"))
    write_json(run_dir / "loop.json", loop.model_dump(mode="json"))
    write_trace(run_dir / "trace.txt", task_id, patch_result, verifier_result, reward)
    append_jsonl(reward, rewards_jsonl)
    append_observation(observation, observations_jsonl)

    artifact_paths = {
        "task": run_dir / "task.md",
        "verifier": run_dir / "verifier.yaml",
        "attempt_patch": run_dir / "attempt.patch",
        "teacher_patch": run_dir / "teacher.patch",
        "trace": run_dir / "trace.txt",
        "reward": run_dir / "reward.json",
        "observation": run_dir / "observation.json",
        "loop": run_dir / "loop.json",
    }
    raw_artifacts = load_files(artifact_paths, lake_root)
    append_manifest(raw_artifacts, manifest_jsonl)

    record = RunRecord(
        run_id=run_id,
        task_id=task_id,
        run_dir=path_text(run_dir),
        workspace_dir=path_text(workspace),
        operator=operator,
        approval_mode=approval_mode,
        verifier=effective_verifier,
        reward=reward,
        loop=loop,
        artifacts={name: path_text(path) for name, path in artifact_paths.items() if path.exists()},
        raw_artifacts={name: artifact.storage_uri for name, artifact in raw_artifacts.items()},
        created_at=utc_now(),
    )
    write_json(run_dir / "run.json", record.model_dump(mode="json"))
    return record


def loop_state(task_id: str, reward: RewardRecord) -> LoopState:
    passed = reward.passed
    return LoopState(
        loop_id=f"loop_{reward.run_id.removeprefix('run_')}",
        goal=task_id,
        recipe=task_id,
        attempts=[
            LoopAttempt(
                run_id=reward.run_id,
                passed=passed,
                reward=reward.reward,
                failure_class=reward.failure_class,
                reason=reward.reason,
            )
        ],
        last_failure=None if passed else reward.reason,
        next_action="promote" if passed else "repair",
        iteration_cap=1,
        stop_reason="verifier_passed" if passed else "iteration_cap_reached",
        updated_at=utc_now(),
    )


def read_verifier(path: Path) -> VerifierSpec:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return VerifierSpec.model_validate(data)


def verifier_command(command: str, workspace: Path) -> str:
    parts = shlex.split(command)
    if not parts or parts[0] not in {"python", "python3"}:
        return command
    if not (workspace / "uv.lock").exists() or shutil.which("uv") is None:
        return command
    return " ".join(shlex.quote(part) for part in ["uv", "run", "--project", ".", *parts])


def copy_required(source: Path, destination: Path) -> None:
    if not source.exists():
        raise ValueError(f"missing required file: {source}")
    shutil.copy2(source, destination)


def copy_workspace(source: Path, destination: Path) -> None:
    if not source.exists():
        raise ValueError(f"missing required repo directory: {source}")
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))


def run_command(command: list[str], cwd: Path, timeout_seconds: int = 30) -> CommandResult:
    started = utc_now()
    env = None
    if command[:2] == ["git", "apply"]:
        env = os.environ | {"GIT_CEILING_DIRECTORIES": path_text(Path(cwd).resolve().parent)}
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout_seconds, check=False, env=env)
    return CommandResult(
        command=" ".join(command),
        cwd=path_text(cwd),
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        started_at=started,
        finished_at=utc_now(),
    )


def run_shell(command: str, cwd: Path, timeout_seconds: int) -> CommandResult:
    started = utc_now()
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, shell=True, capture_output=True, timeout=timeout_seconds, check=False)
        return CommandResult(
            command=command,
            cwd=path_text(cwd),
            exit_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            started_at=started,
            finished_at=utc_now(),
        )
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            command=command,
            cwd=path_text(cwd),
            exit_code=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "verifier timed out",
            started_at=started,
            finished_at=utc_now(),
        )


def patch_result_ok(result: CommandResult | None) -> bool:
    return result is None or result.exit_code == 0


def failure_reason(patch_result: CommandResult | None, verifier_result: CommandResult | None) -> str:
    if patch_result and patch_result.exit_code != 0:
        return f"attempt patch exited {patch_result.exit_code}"
    if verifier_result:
        return f"verifier exited {verifier_result.exit_code}"
    return "verifier did not run"


def write_trace(
    path: Path,
    task_id: str,
    patch_result: CommandResult | None,
    verifier_result: CommandResult | None,
    reward: RewardRecord,
) -> None:
    sections = [f"task_id: {task_id}", f"run_id: {reward.run_id}", ""]
    if patch_result:
        sections.extend(command_section("patch", patch_result))
    if verifier_result:
        sections.extend(command_section("verifier", verifier_result))
    sections.extend(["reward:", json.dumps(reward.model_dump(mode="json"), indent=2), ""])
    path.write_text("\n".join(sections), encoding="utf-8")


def command_section(name: str, result: CommandResult) -> list[str]:
    return [
        f"{name}: {result.command}",
        f"cwd: {result.cwd}",
        f"exit_code: {result.exit_code}",
        "stdout:",
        result.stdout,
        "stderr:",
        result.stderr,
        "",
    ]


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_yaml(path: Path, value: HarnessModel) -> None:
    path.write_text(yaml.safe_dump(value.model_dump(mode="json"), sort_keys=True), encoding="utf-8")


def append_jsonl(model: RewardRecord, path: Path | str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as file:
        file.write(json.dumps(model.model_dump(mode="json"), sort_keys=True) + "\n")
