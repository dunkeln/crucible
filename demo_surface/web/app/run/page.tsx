import Link from "next/link";
import { demoApiBaseUrl, fetchDemoRun } from "../../lib/demo-api";

function RunSection({
  title,
  body
}: {
  title: string;
  body: string;
}) {
  return (
    <article className="detail-card">
      <div className="label">{title}</div>
      <p className="mono">{body}</p>
    </article>
  );
}

export default async function RunPage() {
  const run = await fetchDemoRun();

  return (
    <main className="page-shell">
      <section className="hero">
        <span className="eyebrow">Run View</span>
        <h1>Current demo run, rendered by Next.js.</h1>
        <p>
          This page reads the same JSON payload as the CLI viewer. It is only a
          presentation layer over the Python API.
        </p>
        <div className="action-row">
          <Link className="button primary" href="/">
            Back to landing page
          </Link>
          <a className="button subtle" href={`${demoApiBaseUrl}/runs/demo`}>
            Open raw JSON
          </a>
        </div>
      </section>

      <section className="detail-stack">
        <RunSection title="Task" body={run.task} />
        <RunSection title="Attempt" body={run.attempt} />
        <RunSection title="Verifier Result" body={run.verifier_result} />
        <RunSection title="Reward" body={run.reward} />
        <RunSection title="Teacher Repair" body={run.teacher_repair} />
        <RunSection title="Curated Row Export" body={run.curated_row} />
      </section>
    </main>
  );
}
