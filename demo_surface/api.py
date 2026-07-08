import json
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


DATA_PATH = Path(__file__).with_name("data") / "demo_run.json"


def load_demo_run() -> dict[str, str]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


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
    base_url = f"http://{host}:{port}"
    return render_html_page(
        "Crucible Demo Surface",
        f"""
<main class="shell">
  <section class="hero">
    <span class="eyebrow">Demo Surface</span>
    <h1>Crucible API landing page</h1>
    <p class="hero-copy">
      This surface is the read-only entrypoint for one measured run. You can open the human view,
      inspect the raw JSON, or redirect through the API switch without turning the UI into the source of truth.
    </p>
    <div class="actions">
      <a class="button primary" href="/go?target=view">Open run view</a>
      <a class="button" href="/go?target=json">Open raw JSON</a>
      <a class="button" href="/health">Check health</a>
    </div>
  </section>

  <section class="grid">
    <article class="panel">
      <div class="label">Current status</div>
      <h2>Connected locally</h2>
      <p>The API is live on <span class="mono">{escape(base_url)}</span>.</p>
      <p style="margin-top: 12px;"><span class="status">healthy</span></p>
    </article>

    <article class="panel">
      <div class="label">What this shows</div>
      <h2>One complete evidence loop</h2>
      <p>Task, student attempt, verifier result, reward, teacher repair, and curated row export.</p>
    </article>

    <article class="panel">
      <div class="label">Seam boundary</div>
      <h2>Presentation only</h2>
      <p>The surface reads API output. It does not own verifier logic, model execution, or corpus truth.</p>
    </article>
  </section>

  <section class="stack">
    <article class="panel">
      <div class="label">Routes</div>
      <div class="route-list">
        <div class="route-item">
          <strong class="mono">/</strong>
          Landing page for navigation and status.
        </div>
        <div class="route-item">
          <strong class="mono">/view</strong>
          Human-readable web view of the current demo run.
        </div>
        <div class="route-item">
          <strong class="mono">/runs/demo</strong>
          Raw JSON payload consumed by the CLI viewer.
        </div>
        <div class="route-item">
          <strong class="mono">/go?target=view</strong>
          Redirect helper for browser-oriented viewing.
        </div>
        <div class="route-item">
          <strong class="mono">/go?target=json</strong>
          Redirect helper for API-oriented inspection.
        </div>
        <div class="route-item">
          <strong class="mono">/health</strong>
          Minimal liveness check.
        </div>
      </div>
    </article>

    <article class="grid">
      <div class="panel">
        <div class="label">Current holder</div>
        <h3>Model connection</h3>
        <p>Placeholder only. No inference engine is wired into this API yet.</p>
      </div>
      <div class="panel">
        <div class="label">Current holder</div>
        <h3>Verifier wiring</h3>
        <p>Placeholder only. The payload exposes verifier output but does not run verification.</p>
      </div>
      <div class="panel">
        <div class="label">Current holder</div>
        <h3>Corpus export</h3>
        <p>Placeholder only. The export shape is visible, but promotion logic lives elsewhere.</p>
      </div>
    </article>

    <article class="panel">
      <div class="label">Next integration points</div>
      <ul class="placeholder-list">
        <li>Swap the local JSON file for harness-produced run artifacts.</li>
        <li>Replace the sample row with a math task row once the verifier contract is fixed.</li>
        <li>Keep the same API shape so the CLI and browser views do not need to change.</li>
      </ul>
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
            self.respond_html(render_run_page(load_demo_run()))
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

        if path == "/runs/demo":
            self.respond(load_demo_run())
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
