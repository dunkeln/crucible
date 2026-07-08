from __future__ import annotations

import json
from pathlib import Path

import click

from harness.codex_runtime import run_codex_attempt
from harness.contracts import ApprovalMode, OperatorMode
from harness.operators import CodexOperatorRole, operator_brief
from harness.promote import promote_run
from harness.runner import run_task


@click.group()
def main() -> None:
    """Run the Crucible harness."""


@main.command("run-task")
@click.argument("task_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--attempt-patch", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None)
@click.option("--runs-root", default=".crucible/runs", show_default=True)
@click.option("--lake-root", default=".crucible/lake", show_default=True)
@click.option("--manifest-jsonl", default=".crucible/manifest.jsonl", show_default=True)
@click.option("--rewards-jsonl", default=".crucible/rewards.jsonl", show_default=True)
@click.option("--observations-jsonl", default=".crucible/observations.jsonl", show_default=True)
@click.option("--operator", "operator_value", type=click.Choice([item.value for item in OperatorMode]), default=OperatorMode.HUMAN.value, show_default=True)
@click.option("--approval-mode", type=click.Choice([item.value for item in ApprovalMode]), default=ApprovalMode.MANUAL.value, show_default=True)
@click.option("--promote/--no-promote", default=False, show_default=True)
@click.option("--dataset-root", default=".crucible/dataset", show_default=True)
def run_task_command(
    task_dir: Path,
    attempt_patch: Path | None,
    runs_root: str,
    lake_root: str,
    manifest_jsonl: str,
    rewards_jsonl: str,
    observations_jsonl: str,
    operator_value: str,
    approval_mode: str,
    promote: bool,
    dataset_root: str,
) -> None:
    """Run one task attempt through verifier and reward capture."""
    try:
        record = run_task(
            task_dir=task_dir,
            attempt_patch=attempt_patch,
            runs_root=runs_root,
            lake_root=lake_root,
            manifest_jsonl=manifest_jsonl,
            rewards_jsonl=rewards_jsonl,
            observations_jsonl=observations_jsonl,
            operator=OperatorMode(operator_value),
            approval_mode=ApprovalMode(approval_mode),
        )
        output: dict[str, object] = {"run": record.model_dump(mode="json")}
        if promote:
            output["promotion"] = promote_run(record.run_dir, dataset_root).model_dump(mode="json")
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(output, indent=2, sort_keys=True))


@main.command("promote-run")
@click.argument("run_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--dataset-root", default=".crucible/dataset", show_default=True)
def promote_run_command(run_dir: Path, dataset_root: str) -> None:
    """Promote one completed run into SFT/RLVR rows."""
    try:
        result = promote_run(run_dir, dataset_root)
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result.model_dump_json(indent=2))


@main.command("operator-brief")
@click.argument("role", type=click.Choice([item.value for item in CodexOperatorRole]))
@click.option("--task-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=None)
@click.option("--run-dir", type=click.Path(exists=True, file_okay=False, path_type=Path), default=None)
def operator_brief_command(role: str, task_dir: Path | None, run_dir: Path | None) -> None:
    """Emit a hardcoded Codex operator brief for a task or run."""
    result = operator_brief(CodexOperatorRole(role), task_dir=task_dir, run_dir=run_dir)
    click.echo(result.model_dump_json(indent=2))


@main.command("run-codex-task")
@click.argument("task_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--role", type=click.Choice([item.value for item in CodexOperatorRole]), default=CodexOperatorRole.OPERATOR.value, show_default=True)
@click.option("--model", default=None)
@click.option("--approval-mode", type=click.Choice([item.value for item in ApprovalMode]), default=ApprovalMode.AUTO_SAFE.value, show_default=True)
@click.option("--runs-root", default=".crucible/runs", show_default=True)
@click.option("--lake-root", default=".crucible/lake", show_default=True)
@click.option("--manifest-jsonl", default=".crucible/manifest.jsonl", show_default=True)
@click.option("--rewards-jsonl", default=".crucible/rewards.jsonl", show_default=True)
@click.option("--observations-jsonl", default=".crucible/observations.jsonl", show_default=True)
@click.option("--dataset-root", default=".crucible/dataset", show_default=True)
@click.option("--codex-root", default=".crucible/codex", show_default=True)
@click.option("--promote/--no-promote", default=False, show_default=True)
def run_codex_task_command(
    task_dir: Path,
    role: str,
    model: str | None,
    approval_mode: str,
    runs_root: str,
    lake_root: str,
    manifest_jsonl: str,
    rewards_jsonl: str,
    observations_jsonl: str,
    dataset_root: str,
    codex_root: str,
    promote: bool,
) -> None:
    """Use Codex SDK to create an attempt patch, then run verifier/reward capture."""
    chosen_approval = ApprovalMode(approval_mode)
    try:
        codex_result = run_codex_attempt(
            task_dir=task_dir,
            codex_root=codex_root,
            role=CodexOperatorRole(role),
            approval_mode=chosen_approval,
            model=model,
        )
        record = run_task(
            task_dir=task_dir,
            attempt_patch=Path(codex_result.patch_path),
            runs_root=runs_root,
            lake_root=lake_root,
            manifest_jsonl=manifest_jsonl,
            rewards_jsonl=rewards_jsonl,
            observations_jsonl=observations_jsonl,
            operator=OperatorMode.CODEX,
            approval_mode=chosen_approval,
        )
        output: dict[str, object] = {
            "codex": codex_result.model_dump(mode="json"),
            "run": record.model_dump(mode="json"),
        }
        if promote:
            output["promotion"] = promote_run(record.run_dir, dataset_root).model_dump(mode="json")
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
