import json
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


DATA_PATH = Path(__file__).with_name("data") / "demo_run.json"
RUNS_ROOT = Path("data/runs")


def load_demo_run() -> dict[str, str]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def list_harness_runs() -> list[dict[str, str | int | bool]]:
    if not RUNS_ROOT.exists():
        return []

    runs: list[dict[str, str | int | bool]] = []
    run_dirs = sorted(
        [path for path in RUNS_ROOT.iterdir() if path.is_dir() and (path / "run.json").exists()],
        key=lambda path: (path / "run.json").stat().st_mtime,
        reverse=True,
    )
    for run_dir in run_dirs:
        run_data = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
        reward_data = run_data.get("reward", {})
        runs.append(
            {
                "run_id": str(run_data.get("run_id", run_dir.name)),
                "task_id": str(run_data.get("task_id", "unknown-task")),
                "created_at": str(run_data.get("created_at", "")),
                "passed": bool(reward_data.get("passed", False)),
                "reward": int(reward_data.get("reward", 0)),
            }
        )
    return runs


def _safe_read_text(path: Path | None, default: str = "") -> str:
    if not path:
        return default
    if not path.exists():
        return default
    return path.read_text(encoding="utf-8")


def _path_from_run(run_dir: Path, value: str | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if path.is_absolute():
        return path
    return run_dir / path


def load_harness_run(run_id: str) -> dict[str, str]:
    run_dir = RUNS_ROOT / run_id
    run_path = run_dir / "run.json"
    if not run_path.exists():
        raise FileNotFoundError(run_id)

    run_data = json.loads(run_path.read_text(encoding="utf-8"))
    artifacts = run_data.get("artifacts", {})
    reward = run_data.get("reward", {})
    attempt_patch = _safe_read_text(_path_from_run(run_dir, artifacts.get("attempt_patch")), "attempt patch not found")
    teacher_patch = _safe_read_text(_path_from_run(run_dir, artifacts.get("teacher_patch")), "teacher.patch missing for this run")
    task_text = _safe_read_text(_path_from_run(run_dir, artifacts.get("task")), "task.md missing")
    observation_text = _safe_read_text(_path_from_run(run_dir, artifacts.get("observation")), "")
    observation = json.loads(observation_text) if observation_text else {}

    verifier_result = (
        f"{'PASS' if reward.get('passed') else 'FAIL'}\n"
        f"- pattern: {observation.get('pattern_id', 'unknown')}\n"
        f"- reason: {reward.get('reason', 'no reason available')}\n"
        f"- exit_code: {reward.get('exit_code', 'unknown')}"
    )
    reward_text = (
        f"Reward: {reward.get('reward', 0)}\n"
        f"Reason: {reward.get('reason', 'no reason available')}"
    )
    curated_row = json.dumps(
        {
            "run_id": run_data.get("run_id"),
            "task_id": run_data.get("task_id"),
            "passed": reward.get("passed"),
            "reward": reward.get("reward"),
        }
    )
    return {
        "task": task_text.strip(),
        "attempt": attempt_patch.strip(),
        "verifier_result": verifier_result,
        "reward": reward_text,
        "teacher_repair": teacher_patch.strip(),
        "curated_row": curated_row,
    }


def load_default_run() -> dict[str, str]:
    runs = list_harness_runs()
    if runs:
        latest_run_id = str(runs[0]["run_id"])
        return load_harness_run(latest_run_id)
    return load_demo_run()


def render_html_page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <style>
    :root {{
      --bg: #f4efe4;
      --panel: #fffaf1;
      --ink: #1f2a2d;
      --muted: #5d6a6d;
      --accent: #a63d1f;
      --accent-soft: #f3d9c7;
      --line: #d7c8b2;
      --shadow: rgba(31, 42, 45, 0.12);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: "Trebuchet MS", "Segoe UI", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, #fff8ef 0, #f4efe4 46%, #eadfce 100%);
    }}

    a {{
      color: inherit;
    }}

    .shell {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }}

    .hero {{
      background: linear-gradient(135deg, #fffaf1 0%, #f6ebd8 100%);
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 28px;
      box-shadow: 0 20px 50px var(--shadow);
    }}

    .eyebrow {{
      display: inline-block;
      margin-bottom: 14px;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    h1, h2, h3 {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
    }}

    h1 {{
      font-size: clamp(2.2rem, 4vw, 4rem);
      line-height: 1;
    }}

    p {{
      margin: 0;
      line-height: 1.6;
    }}

    .hero-copy {{
      margin-top: 18px;
      max-width: 720px;
      color: var(--muted);
      font-size: 1.05rem;
    }}

    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 24px;
    }}

    .button {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 44px;
      padding: 0 16px;
      border-radius: 999px;
      border: 1px solid var(--ink);
      text-decoration: none;
      font-weight: 700;
      background: transparent;
    }}

    .button.primary {{
      background: var(--ink);
      color: #fffaf1;
      border-color: var(--ink);
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
      margin-top: 20px;
    }}

    .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 20px;
      padding: 20px;
      box-shadow: 0 12px 30px rgba(31, 42, 45, 0.08);
    }}

    .panel h2, .panel h3 {{
      margin-bottom: 10px;
    }}

    .label {{
      margin-bottom: 10px;
      color: var(--accent);
      font-weight: 700;
      text-transform: uppercase;
      font-size: 0.8rem;
      letter-spacing: 0.06em;
    }}

    .mono {{
      font-family: Consolas, "Courier New", monospace;
      white-space: pre-wrap;
      word-break: break-word;
    }}

    .stack {{
      display: grid;
      gap: 16px;
      margin-top: 20px;
    }}

    .route-list {{
      display: grid;
      gap: 10px;
    }}

    .route-item {{
      padding: 12px 14px;
      border-radius: 14px;
      background: #fff;
      border: 1px solid var(--line);
    }}

    .route-item strong {{
      display: block;
      margin-bottom: 4px;
    }}

    .status {{
      display: inline-block;
      padding: 4px 8px;
      border-radius: 999px;
      background: #dbeee0;
      color: #1b6b39;
      font-size: 0.85rem;
      font-weight: 700;
    }}

    .placeholder-list {{
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
    }}

    .placeholder-list li + li {{
      margin-top: 8px;
    }}
  </style>
</head>
<body>
  {body}
</body>
</html>
"""


def render_landing_page(host: str, port: int) -> str:
    runs = list_harness_runs()
    if runs:
        run_items = "".join(
            f"""
        <div class="route-item">
          <strong class="mono">{escape(str(run["run_id"]))}</strong>
          task: {escape(str(run["task_id"]))} | reward: {escape(str(run["reward"]))} | passed: {escape(str(run["passed"]))}
        </div>
"""
            for run in runs[:8]
        )
    else:
        run_items = """
        <div class="route-item">
          <strong class="mono">No runs yet</strong>
        </div>
"""
    return render_html_page(
        "Crucible Demo Surface",
        f"""
<main class="shell">
  <section class="hero">
    <span class="eyebrow">Crucible</span>
    <h1>A model can try a thousand times a second. A person can only check so many.</h1>
    <p class="hero-copy">
      Crucible does the checking the same way every time, so the pile of tries turns into
      lessons worth keeping without a person grading each answer by hand.
    </p>
    <div class="actions">
      <a class="button primary" href="/go?target=view">See one run</a>
      <a class="button" href="/go?target=json">Open the raw data</a>
    </div>
  </section>

  <section class="grid">
    <article class="panel">
      <div class="label">The slow part</div>
      <h2>The person is the ceiling</h2>
      <p>The model can try a million times. But if one person has to look at every answer, the
      pile only shrinks as fast as one tired human.</p>
    </article>

    <article class="panel">
      <div class="label">The move</div>
      <h2>Repeat the boring part</h2>
      <p>The model tries. A checker says right or wrong. A score says how good. A fix shows the
      better way. Each try is saved as a small lesson.</p>
    </article>

    <article class="panel">
      <div class="label">Why trust it</div>
      <h2>A test, not a hunch</h2>
      <p>Every score comes from a check written before the model ever runs. The answer passes or
      it does not, so a failed try is proof, not trash.</p>
    </article>
  </section>

  <section class="stack">
    <article class="panel">
      <div class="label">Runs the machine already made</div>
      <div class="route-list">
        {run_items}
      </div>
    </article>
  </section>
</main>
""",
    )


def render_run_page(run: dict[str, str]) -> str:
    def section(title: str, body: str) -> str:
        return f"""
<article class="panel">
  <div class="label">{escape(title)}</div>
  <p class="mono">{escape(body)}</p>
</article>
"""

    return render_html_page(
        "Crucible Run View",
        f"""
<main class="shell">
  <section class="hero">
    <span class="eyebrow">Run View</span>
    <h1>Current demo run</h1>
    <p class="hero-copy">
      This page renders the same run that the CLI viewer fetches from the JSON API.
      Use it for quick visual inspection in a browser.
    </p>
    <div class="actions">
      <a class="button primary" href="/runs/demo">Open raw JSON</a>
      <a class="button" href="/">Back to landing page</a>
    </div>
  </section>

  <section class="stack">
    {section("Task", run["task"])}
    {section("Attempt", run["attempt"])}
    {section("Verifier Result", run["verifier_result"])}
    {section("Reward", run["reward"])}
    {section("Teacher Repair", run["teacher_repair"])}
    {section("Curated Row Export", run["curated_row"])}
  </section>
</main>
""",
    )


class DemoSurfaceHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/":
            self.respond_html(render_landing_page(*self.server.server_address))
            return

        if path == "/view":
            self.respond_html(render_run_page(load_default_run()))
            return

        if path == "/go":
            target = query.get("target", ["view"])[0]
            if target == "json":
                self.redirect("/runs/demo")
                return

            self.redirect("/view")
            return

        if path == "/health":
            self.respond({"status": "ok"})
            return

        if path == "/runs":
            self.respond({"runs": list_harness_runs()})
            return

        if path == "/runs/demo":
            run_id = query.get("run_id", [None])[0]
            if run_id:
                try:
                    self.respond(load_harness_run(run_id))
                except FileNotFoundError:
                    self.respond({"error": f"run not found: {run_id}"}, status=HTTPStatus.NOT_FOUND)
                return

            self.respond(load_default_run())
            return

        if path.startswith("/runs/"):
            run_id = path.removeprefix("/runs/").strip()
            if not run_id or run_id == "demo":
                self.respond({"error": "run_id is required"}, status=HTTPStatus.BAD_REQUEST)
                return

            try:
                self.respond(load_harness_run(run_id))
            except FileNotFoundError:
                self.respond({"error": f"run not found: {run_id}"}, status=HTTPStatus.NOT_FOUND)
            return

        self.respond({"error": "not found"}, status=HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:
        return

    def respond(self, payload: dict[str, str], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def respond_html(self, page: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = page.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        self.end_headers()


def serve(host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), DemoSurfaceHandler)
    print(f"Demo surface API listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    serve()
