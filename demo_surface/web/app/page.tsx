import Link from "next/link";
import { demoApiBaseUrl, fetchHealth } from "../lib/demo-api";

function RouteCard({
  route,
  description
}: {
  route: string;
  description: string;
}) {
  return (
    <div className="route-card">
      <strong>{route}</strong>
      <span>{description}</span>
    </div>
  );
}

export default async function LandingPage() {
  let apiHealthy = false;

  try {
    const health = await fetchHealth();
    apiHealthy = health.status === "ok";
  } catch {
    apiHealthy = false;
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <span className="eyebrow">Demo Surface</span>
        <h1>Crucible landing page, now in Next.js.</h1>
        <p>
          This frontend stays in the presentation seam. It reads the Python API,
          exposes the current run clearly, and leaves model execution, verifier
          logic, and corpus promotion outside the UI boundary.
        </p>
        <div className="action-row">
          <Link className="button primary" href="/run">
            Open run view
          </Link>
          <a className="button subtle" href={`${demoApiBaseUrl}/runs/demo`}>
            Open raw JSON
          </a>
          <a className="button subtle" href={`${demoApiBaseUrl}/health`}>
            Check API health
          </a>
        </div>
      </section>

      <section className="status-strip">
        <article className="card">
          <div className="label">API status</div>
          <h3>{apiHealthy ? "Connected locally" : "API not reachable"}</h3>
          <p>
            Base URL: <span className="mono">{demoApiBaseUrl}</span>
          </p>
          <p style={{ marginTop: 14 }}>
            <span className="status-pill">
              {apiHealthy ? "healthy" : "offline"}
            </span>
          </p>
        </article>

        <article className="card">
          <div className="label">Current loop</div>
          <h3>One measured run</h3>
          <p>
            Task, attempt, verifier result, reward, teacher repair, and curated
            row export are all reachable from the same API boundary.
          </p>
        </article>

        <article className="card">
          <div className="label">Seam guard</div>
          <h3>Presentation only</h3>
          <p>
            The frontend renders API output. It does not become the source of
            truth for judging a run.
          </p>
        </article>
      </section>

      <section className="split-grid">
        <div className="detail-card">
          <div className="label">Routes</div>
          <h2 className="section-title">Available entrypoints</h2>
          <p className="section-copy">
            The Next.js app gives you a browser-first landing page, while the
            Python service keeps the JSON endpoints stable for CLI and future
            harness integration.
          </p>
          <div className="route-list">
            <RouteCard route="/" description="This Next.js landing page." />
            <RouteCard route="/run" description="Human-readable run view in Next.js." />
            <RouteCard
              route={`${demoApiBaseUrl}/runs/demo`}
              description="Raw JSON payload from the Python API."
            />
            <RouteCard
              route={`${demoApiBaseUrl}/health`}
              description="Liveness check for the Python API."
            />
            <RouteCard
              route={`${demoApiBaseUrl}/view`}
              description="Existing Python-rendered HTML view, kept for parity."
            />
          </div>
        </div>

        <div className="detail-stack">
          <article className="detail-card">
            <div className="label">Necessary holder</div>
            <h3>Model connection</h3>
            <p>
              Placeholder only. A future harness can replace the static JSON with
              model-produced run artifacts without changing the frontend shape.
            </p>
          </article>

          <article className="detail-card">
            <div className="label">Necessary holder</div>
            <h3>Verifier wiring</h3>
            <p>
              Placeholder only. The UI surfaces verifier output but does not own
              how that judgment is computed.
            </p>
          </article>

          <article className="detail-card">
            <div className="label">Necessary holder</div>
            <h3>Corpus export</h3>
            <p>
              Placeholder only. Promotion into durable dataset rows stays outside
              the landing page.
            </p>
          </article>
        </div>
      </section>

      <section className="section-block">
        <h2 className="section-title">What to do next</h2>
        <p className="section-copy">
          Keep the frontend small. The next useful changes are API-side:
          replacing the local sample row with harness output, then introducing a
          single math-task contract with an objective verifier.
        </p>
        <ul className="note-list">
          <li>Swap the JSON file for a harness-produced artifact.</li>
          <li>Keep the same run payload shape for both CLI and browser views.</li>
          <li>Only add model execution after the verifier contract is fixed.</li>
        </ul>
        <p className="footer-note">
          If the API is not running, start it with{" "}
          <span className="mono">python -m demo_surface.api</span>.
        </p>
      </section>
    </main>
  );
}
