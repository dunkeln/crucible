from __future__ import annotations

import json
import re
from pathlib import Path

import click

from harness.codex_runtime import run_codex_attempt
from harness.contracts import ApprovalMode, OperatorMode
from harness.operators import CodexOperatorRole, operator_brief
from harness.promote import promote_run
from harness.runner import run_task
from harness.scaffold import DEFAULT_MODEL, scaffold_math_rlvr


@click.group()
def main() -> None:
    """Run the Crucible harness."""


@main.command("run-task")
@click.argument("task_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--attempt-patch", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None)
@click.option("--project", default=None, help="Project namespace for Crucible artifacts.")
@click.option("--crucible-root", default=".crucible", show_default=True)
@click.option("--runs-root", default=None)
@click.option("--lake-root", default=None)
@click.option("--manifest-jsonl", default=None)
@click.option("--rewards-jsonl", default=None)
@click.option("--observations-jsonl", default=None)
@click.option("--operator", "operator_value", type=click.Choice([item.value for item in OperatorMode]), default=OperatorMode.HUMAN.value, show_default=True)
@click.option("--approval-mode", type=click.Choice([item.value for item in ApprovalMode]), default=ApprovalMode.MANUAL.value, show_default=True)
@click.option("--promote/--no-promote", default=False, show_default=True)
@click.option("--dataset-root", default=None)
def run_task_command(
    task_dir: Path,
    attempt_patch: Path | None,
    project: str | None,
    crucible_root: str,
    runs_root: str | None,
    lake_root: str | None,
    manifest_jsonl: str | None,
    rewards_jsonl: str | None,
    observations_jsonl: str | None,
    operator_value: str,
    approval_mode: str,
    promote: bool,
    dataset_root: str | None,
) -> None:
    """Run one task attempt through verifier and reward capture."""
    try:
        paths = project_paths(task_dir, project, crucible_root)
        record = run_task(
            task_dir=task_dir,
            attempt_patch=attempt_patch,
            runs_root=runs_root or paths["runs"],
            lake_root=lake_root or paths["lake"],
            manifest_jsonl=manifest_jsonl or paths["manifest"],
            rewards_jsonl=rewards_jsonl or paths["rewards"],
            observations_jsonl=observations_jsonl or paths["observations"],
            operator=OperatorMode(operator_value),
            approval_mode=ApprovalMode(approval_mode),
        )
        output: dict[str, object] = {"run": record.model_dump(mode="json")}
        if promote:
            output["promotion"] = promote_run(record.run_dir, dataset_root or paths["dataset"]).model_dump(mode="json")
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


@main.group("scaffold")
def scaffold_command() -> None:
    """Write deterministic project scaffolds."""


@scaffold_command.command("math-rlvr")
@click.option("--root", type=click.Path(file_okay=False, path_type=Path), default=".", show_default=True)
@click.option("--package", "package_name", default="crucible_demos", show_default=True)
@click.option("--model", default=DEFAULT_MODEL, show_default=True)
@click.option("--force/--no-force", default=False, show_default=True)
def scaffold_math_rlvr_command(root: Path, package_name: str, model: str, force: bool) -> None:
    """Create a tiny exact-answer math RLVR scaffold."""
    try:
        result = scaffold_math_rlvr(root, package_name, model, force)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2, sort_keys=True))


@main.command("run-codex-task")
@click.argument("task_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--role", type=click.Choice([item.value for item in CodexOperatorRole]), default=CodexOperatorRole.OPERATOR.value, show_default=True)
@click.option("--model", default=None)
@click.option("--approval-mode", type=click.Choice([item.value for item in ApprovalMode]), default=ApprovalMode.AUTO_SAFE.value, show_default=True)
@click.option("--project", default=None, help="Project namespace for Crucible artifacts.")
@click.option("--crucible-root", default=".crucible", show_default=True)
@click.option("--runs-root", default=None)
@click.option("--lake-root", default=None)
@click.option("--manifest-jsonl", default=None)
@click.option("--rewards-jsonl", default=None)
@click.option("--observations-jsonl", default=None)
@click.option("--dataset-root", default=None)
@click.option("--codex-root", default=None)
@click.option("--promote/--no-promote", default=False, show_default=True)
def run_codex_task_command(
    task_dir: Path,
    role: str,
    model: str | None,
    approval_mode: str,
    project: str | None,
    crucible_root: str,
    runs_root: str | None,
    lake_root: str | None,
    manifest_jsonl: str | None,
    rewards_jsonl: str | None,
    observations_jsonl: str | None,
    dataset_root: str | None,
    codex_root: str | None,
    promote: bool,
) -> None:
    """Use Codex SDK to create an attempt patch, then run verifier/reward capture."""
    chosen_approval = ApprovalMode(approval_mode)
    try:
        paths = project_paths(task_dir, project, crucible_root)
        codex_result = run_codex_attempt(
            task_dir=task_dir,
            codex_root=codex_root or paths["codex"],
            role=CodexOperatorRole(role),
            approval_mode=chosen_approval,
            model=model,
        )
        record = run_task(
            task_dir=task_dir,
            attempt_patch=Path(codex_result.patch_path),
            runs_root=runs_root or paths["runs"],
            lake_root=lake_root or paths["lake"],
            manifest_jsonl=manifest_jsonl or paths["manifest"],
            rewards_jsonl=rewards_jsonl or paths["rewards"],
            observations_jsonl=observations_jsonl or paths["observations"],
            operator=OperatorMode.CODEX,
            approval_mode=chosen_approval,
        )
        output: dict[str, object] = {
            "codex": codex_result.model_dump(mode="json"),
            "run": record.model_dump(mode="json"),
        }
        if promote:
            output["promotion"] = promote_run(record.run_dir, dataset_root or paths["dataset"]).model_dump(mode="json")
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(output, indent=2, sort_keys=True))


def project_paths(task_dir: Path, project: str | None, crucible_root: str) -> dict[str, Path]:
    root = Path(crucible_root) / "projects" / project_slug(task_dir, project)
    return {
        "runs": root / "runs",
        "lake": root / "lake",
        "manifest": root / "manifest.jsonl",
        "rewards": root / "rewards.jsonl",
        "observations": root / "observations.jsonl",
        "dataset": root / "dataset",
        "codex": root / "codex",
    }


def project_slug(task_dir: Path, project: str | None = None) -> str:
    if project:
        return slug(project)
    resolved = task_dir.resolve()
    for parent in resolved.parents:
        if parent.name == ".crucible":
            return slug(parent.parent.name)
    return slug(Path.cwd().resolve().name)


def slug(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip().lower()).strip("-._")
    return cleaned or "default"


if __name__ == "__main__":
    main()
