from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from harness.contracts import ApprovalMode, HarnessModel, path_text
from harness.operators import CodexOperatorRole, operator_brief
from harness.runner import read_verifier


class CodexAttemptResult(HarnessModel):
    role: CodexOperatorRole
    approval_mode: ApprovalMode
    sdk_approval_mode: str
    sandbox: str
    model: str | None
    thread_id: str
    status: str
    final_response: str | None
    workspace_dir: str
    patch_path: str
    patch_created: bool


def run_codex_attempt(
    task_dir: Path | str,
    *,
    codex_root: Path | str = "data/codex",
    role: CodexOperatorRole = CodexOperatorRole.OPERATOR,
    approval_mode: ApprovalMode = ApprovalMode.AUTO_SAFE,
    model: str | None = None,
) -> CodexAttemptResult:
    codex_sdk = load_codex_sdk()
    task_path = Path(task_dir)
    verifier = read_verifier(task_path / "verifier.yaml")
    brief = operator_brief(role, task_dir=task_path)

    workspace_root = Path(codex_root) / new_codex_id()
    repo_workspace = workspace_root / "repo"
    patch_path = workspace_root / "attempt.patch"
    meta_path = workspace_root / "codex.json"

    copy_workspace(task_path / "repo", repo_workspace)
    init_workspace_repo(repo_workspace)

    sdk_approval = map_approval_mode(codex_sdk, approval_mode)
    sdk_sandbox = map_sandbox(codex_sdk, role)
    model_candidates = [model] if model else ["gpt-5.3-codex", "gpt-5.4-mini", "gpt-5.4", "gpt-5.2", None]
    model_errors: list[str] = []
    thread = None
    result = None
    selected_model = model
    client = codex_sdk.Codex(codex_sdk.CodexConfig(cwd=path_text(repo_workspace)))
    try:
        for candidate in model_candidates:
            try:
                thread = client.thread_start(
                    approval_mode=sdk_approval,
                    sandbox=sdk_sandbox,
                    cwd=path_text(repo_workspace),
                    model=candidate,
                    developer_instructions=brief.prompt,
                )
                result = thread.run(
                    codex_task_prompt(path_text(repo_workspace), verifier.command),
                    approval_mode=sdk_approval,
                    sandbox=sdk_sandbox,
                    cwd=path_text(repo_workspace),
                    model=candidate,
                )
                selected_model = candidate
                break
            except Exception as exc:
                if model or not is_model_error(exc):
                    raise ValueError(f"codex runtime failed: {exc}") from exc
                model_errors.append(f"{candidate or 'default'}: {exc}")
        if result is None:
            detail = "; ".join(model_errors) if model_errors else "no candidate model succeeded"
            raise ValueError(f"codex runtime failed after model fallback: {detail}")
    finally:
        client.close()

    patch_text = run_command(["git", "diff", "--binary", "--", "."], repo_workspace)
    patch_created = bool(patch_text.strip())
    if patch_created:
        patch_path.write_text(ensure_trailing_newline(patch_text), encoding="utf-8")

    output = CodexAttemptResult(
        role=role,
        approval_mode=approval_mode,
        sdk_approval_mode=sdk_approval.value,
        sandbox=sdk_sandbox.value,
        model=selected_model,
        thread_id=thread.id if thread else "",
        status=result.status.value,
        final_response=result.final_response,
        workspace_dir=path_text(workspace_root),
        patch_path=path_text(patch_path),
        patch_created=patch_created,
    )
    meta_path.write_text(output.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return output


def codex_task_prompt(repo_workspace: str, verifier_command: str) -> str:
    return "\n".join(
        [
            f"Repository root: {repo_workspace}",
            "Make the smallest edit that satisfies the task and passes verifier.",
            f"Verifier command: {verifier_command}",
            "Constraints:",
            "- Edit only files in this repository.",
            "- Do not install dependencies.",
            "- Run the verifier command once before finishing.",
            "Return a short summary of what changed and verifier outcome.",
        ]
    )


def ensure_trailing_newline(value: str) -> str:
    return value if value.endswith("\n") else value + "\n"


def is_model_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "model" in text and any(part in text for part in ("not exist", "not found", "does not have access"))


def map_approval_mode(codex_sdk: object, approval_mode: ApprovalMode):
    if approval_mode is ApprovalMode.AUTO_SAFE:
        return codex_sdk.ApprovalMode.auto_review
    return codex_sdk.ApprovalMode.deny_all


def map_sandbox(codex_sdk: object, role: CodexOperatorRole):
    if role is CodexOperatorRole.RESEARCH_ASSISTANT:
        return codex_sdk.Sandbox.read_only
    return codex_sdk.Sandbox.workspace_write


def new_codex_id() -> str:
    import secrets

    return f"codex-{secrets.token_hex(4)}"


def copy_workspace(source: Path, destination: Path) -> None:
    if not source.exists():
        raise ValueError(f"missing required repo directory: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"))


def init_workspace_repo(repo_workspace: Path) -> None:
    run_command(["git", "init", "-q"], repo_workspace)
    run_command(["git", "add", "-A"], repo_workspace)
    run_command(
        ["git", "commit", "-q", "-m", "baseline"],
        repo_workspace,
        env={
            "GIT_AUTHOR_NAME": "crucible",
            "GIT_AUTHOR_EMAIL": "crucible@example.com",
            "GIT_COMMITTER_NAME": "crucible",
            "GIT_COMMITTER_EMAIL": "crucible@example.com",
        },
    )


def run_command(command: list[str], cwd: Path, env: dict[str, str] | None = None) -> str:
    process_env = dict(**(env or {}))
    completed = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        env={**os.environ, **process_env},
    )
    if completed.returncode != 0:
        raise ValueError(f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stderr.strip()}")
    return completed.stdout


def load_codex_sdk():
    try:
        import openai_codex as codex_sdk
    except ImportError as exc:
        raise ValueError("openai-codex is not installed. Run `uv sync --extra codex`.") from exc
    return codex_sdk
