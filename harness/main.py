from __future__ import annotations

import json
import re
from pathlib import Path

import click

from harness.codex_runtime import codex_attempt_summary, run_codex_attempt
from harness.contracts import ApprovalMode, OperatorMode, path_text
from harness.operators import CodexOperatorRole, operator_brief
from harness.packs import append_rows, benchmark_row, list_runs, read_pack, read_run, run_summary, timed_run, write_pack
from harness.promote import promote_run
from harness.runner import run_task
from harness.scaffold import DEFAULT_MODEL, scaffold_math_rlvr


@click.group()
def main() -> None:
    """Run the Crucible harness."""


@main.command("doctor")
@click.option("--root", type=click.Path(file_okay=False, path_type=Path), default=None)
def doctor_command(root: Path | None) -> None:
    """Check plugin and harness package shape."""
    checks = doctor_checks(root or plugin_root())
    passed = all(check["passed"] for check in checks)
    click.echo(json.dumps({"passed": passed, "checks": checks, "next": doctor_next_steps(passed)}, indent=2, sort_keys=True))
    if not passed:
        raise click.exceptions.Exit(1)


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
@click.option("--json-full/--summary", default=False, show_default=True, help="Print the full run record instead of compact evidence.")
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
    json_full: bool,
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
        output: dict[str, object] = {"run": record.model_dump(mode="json") if json_full else run_summary(record)}
        if promote:
            output["promotion"] = promote_run(record.run_dir, dataset_root or paths["dataset"]).model_dump(mode="json")
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps(output, indent=2, sort_keys=True))


@main.command("lock-pack")
@click.argument("task_dirs", nargs=-1, required=True, type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--output", "output_path", type=click.Path(dir_okay=False, path_type=Path), default=".crucible/pack.lock.json", show_default=True)
def lock_pack_command(task_dirs: tuple[Path, ...], output_path: Path) -> None:
    """Write a task-pack lockfile so future runs skip discovery."""
    try:
        pack = write_pack(task_dirs, output_path)
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps({"pack": path_text(output_path), **pack}, indent=2, sort_keys=True))


@main.command("run-pack")
@click.argument("pack_path", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--arm", default="with_crucible", show_default=True)
@click.option("--project", default=None, help="Project namespace for Crucible artifacts.")
@click.option("--crucible-root", default=".crucible", show_default=True)
@click.option("--operator", "operator_value", type=click.Choice([item.value for item in OperatorMode]), default=OperatorMode.HUMAN.value, show_default=True)
@click.option("--approval-mode", type=click.Choice([item.value for item in ApprovalMode]), default=ApprovalMode.MANUAL.value, show_default=True)
@click.option("--promote/--no-promote", default=False, show_default=True)
@click.option("--dataset-root", default=None)
@click.option("--runs-csv", type=click.Path(dir_okay=False, path_type=Path), default=None)
@click.option("--json-full/--summary", default=False, show_default=True, help="Print full run records instead of the compact summary.")
def run_pack_command(
    pack_path: Path,
    arm: str,
    project: str | None,
    crucible_root: str,
    operator_value: str,
    approval_mode: str,
    promote: bool,
    dataset_root: str | None,
    runs_csv: Path | None,
    json_full: bool,
) -> None:
    """Replay a locked task pack without rediscovering task shape."""
    try:
        pack = read_pack(pack_path)
        rows = []
        runs = []
        summaries = []
        for task in pack["tasks"]:
            task_dir = resolve_pack_task_dir(pack_path, str(task["task_dir"]))
            paths = project_paths(task_dir, project, crucible_root)
            record, wall_seconds = timed_run(
                lambda task_dir=task_dir, paths=paths: run_task(
                    task_dir=task_dir,
                    runs_root=paths["runs"],
                    lake_root=paths["lake"],
                    manifest_jsonl=paths["manifest"],
                    rewards_jsonl=paths["rewards"],
                    observations_jsonl=paths["observations"],
                    operator=OperatorMode(operator_value),
                    approval_mode=ApprovalMode(approval_mode),
                )
            )
            promotion = None
            if promote:
                promotion = promote_run(record.run_dir, dataset_root or paths["dataset"]).model_dump(mode="json")
            row = benchmark_row(record.task_id, arm, Path(record.run_dir), wall_seconds)
            rows.append(row)
            runs.append({"run": record.model_dump(mode="json"), "wall_seconds": row["wall_seconds"], "promotion": promotion})
            summaries.append(run_summary(record, str(row["wall_seconds"])))
        if runs_csv:
            append_rows(runs_csv, rows)
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    output = {"pack": path_text(pack_path), "passed": sum(1 for item in summaries if item["passed"]), "failed": sum(1 for item in summaries if not item["passed"]), "runs": summaries}
    if runs_csv:
        output["runs_csv"] = path_text(runs_csv)
    if json_full:
        output["runs"] = runs
        output["rows"] = rows
    click.echo(json.dumps(output, indent=2, sort_keys=True))


@main.command("list-runs")
@click.option("--project", default=None, help="Project namespace for Crucible artifacts.")
@click.option("--crucible-root", default=".crucible", show_default=True)
@click.option("--limit", default=10, show_default=True, type=click.IntRange(1, 100))
@click.option("--json-full/--summary", default=False, show_default=True, help="Print full run records instead of compact evidence.")
def list_runs_command(project: str | None, crucible_root: str, limit: int, json_full: bool) -> None:
    """List recent runs without manually walking artifact folders."""
    try:
        records = list_runs(Path(crucible_root), project=slug(project) if project else None, limit=limit)
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    runs = [record.model_dump(mode="json") if json_full else run_summary(record) for record in records]
    click.echo(json.dumps({"runs": runs}, indent=2, sort_keys=True))


@main.command("summarize-run")
@click.argument("run_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--json-full/--summary", default=False, show_default=True, help="Print the full run record instead of compact evidence.")
def summarize_run_command(run_dir: Path, json_full: bool) -> None:
    """Summarize an existing run without reading every artifact."""
    try:
        record = read_run(run_dir)
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    output = record.model_dump(mode="json") if json_full else run_summary(record)
    click.echo(json.dumps(output, indent=2, sort_keys=True))


@main.command("promote-run")
@click.argument("run_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--dataset-root", default=".crucible/dataset", show_default=True)
def promote_run_command(run_dir: Path, dataset_root: str) -> None:
    """Promote one completed run into learning rows."""
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
@click.option("--json-full/--summary", default=False, show_default=True, help="Print full Codex and run records instead of compact evidence.")
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
    json_full: bool,
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
            "codex": codex_result.model_dump(mode="json") if json_full else codex_attempt_summary(codex_result),
            "run": record.model_dump(mode="json") if json_full else run_summary(record),
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


def plugin_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_pack_task_dir(pack_path: Path, task_dir: str) -> Path:
    path = Path(task_dir)
    if path.is_absolute() or path.exists():
        return path
    for base in (plugin_root(), pack_path.parent):
        candidate = base / path
        if candidate.exists():
            return candidate
    return path


def doctor_checks(root: Path) -> list[dict[str, object]]:
    manifest_path = root / ".codex-plugin" / "plugin.json"
    manifest = load_json(manifest_path)
    marketplace = load_json(root / ".agents" / "plugins" / "marketplace.json")
    marketplace_path = ((marketplace.get("plugins") or [{}])[0].get("source") or {}).get("path")
    return [
        path_check("plugin manifest", manifest_path),
        value_check("manifest name", manifest.get("name") == "crucible", manifest.get("name")),
        path_check("canonical skill", root / manifest.get("skills", "./skills/") / "crucible" / "SKILL.md"),
        path_check("logo", root / manifest.get("interface", {}).get("logo", "")),
        path_check("composer icon", root / manifest.get("interface", {}).get("composerIcon", "")),
        missing_path_check("no duplicate plugin skills", root / ".codex-plugin" / "skills"),
        missing_path_check("no duplicate plugin assets", root / ".codex-plugin" / "assets"),
        value_check("marketplace path", marketplace_path == "./", marketplace_path),
        path_check("harness entrypoint", root / "crucible"),
        path_check("benchmark pack", root / "harness" / "examples" / "benchmark-pack.lock.json"),
    ]


def doctor_next_steps(passed: bool) -> list[str]:
    command = path_text(plugin_root() / "crucible")
    pack = path_text(plugin_root() / "harness" / "examples" / "benchmark-pack.lock.json")
    if not passed:
        return ["fix failed checks", f"{command} doctor"]
    return [
        f"{command} run-pack {pack} --project smoke",
        f"{command} list-runs --project smoke --limit 5",
    ]


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def path_check(name: str, path: Path) -> dict[str, object]:
    return {"name": name, "passed": path.exists(), "detail": path_text(path)}


def missing_path_check(name: str, path: Path) -> dict[str, object]:
    return {"name": name, "passed": not path.exists(), "detail": path_text(path)}


def value_check(name: str, passed: bool, detail: object) -> dict[str, object]:
    return {"name": name, "passed": passed, "detail": detail}


if __name__ == "__main__":
    main()
