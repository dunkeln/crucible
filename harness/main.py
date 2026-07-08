from __future__ import annotations

import json
from pathlib import Path

import click

from harness.contracts import ApprovalMode, OperatorMode
from harness.hf_dataset import export_hf_dataset
from harness.promote import promote_run
from harness.runner import run_task


@click.group()
def main() -> None:
    """Run the Crucible harness."""


@main.command("run-task")
@click.argument("task_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--attempt-patch", type=click.Path(exists=True, dir_okay=False, path_type=Path), default=None)
@click.option("--runs-root", default="data/runs", show_default=True)
@click.option("--lake-root", default="data/lake", show_default=True)
@click.option("--manifest-jsonl", default="data/manifest.jsonl", show_default=True)
@click.option("--rewards-jsonl", default="data/rewards.jsonl", show_default=True)
@click.option("--observations-jsonl", default="data/observations.jsonl", show_default=True)
@click.option("--operator", "operator_value", type=click.Choice([item.value for item in OperatorMode]), default=OperatorMode.HUMAN.value, show_default=True)
@click.option("--approval-mode", type=click.Choice([item.value for item in ApprovalMode]), default=ApprovalMode.MANUAL.value, show_default=True)
@click.option("--promote/--no-promote", default=False, show_default=True)
@click.option("--dataset-root", default="data/dataset", show_default=True)
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
@click.option("--dataset-root", default="data/dataset", show_default=True)
def promote_run_command(run_dir: Path, dataset_root: str) -> None:
    """Promote one completed run into SFT/RLVR rows."""
    try:
        result = promote_run(run_dir, dataset_root)
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result.model_dump_json(indent=2))


@main.command("export-hf-dataset")
@click.argument("source_root", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output-root", default="datasets/crucible-demo", show_default=True)
@click.option("--validation-size", default=1, show_default=True, type=int)
def export_hf_dataset_command(source_root: Path, output_root: str, validation_size: int) -> None:
    """Export runtime task artifacts into the HF-compatible dataset shape."""
    try:
        result = export_hf_dataset(source_root, output_root, validation_size)
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
