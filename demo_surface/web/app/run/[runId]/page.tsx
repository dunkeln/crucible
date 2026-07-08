import Link from "next/link";
import { demoApiBaseUrl, fetchDemoRunById } from "../../../lib/demo-api";

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

export default async function RunByIdPage({
  params
}: {
  params: { runId: string };
}) {
  const run = await fetchDemoRunById(params.runId);

  return (
    <main className="page-shell">
      <section className="hero">
        <span className="eyebrow">Run View</span>
        <h1>Harness run {params.runId}</h1>
        <p>
          This view is sourced from the harness-backed API route for a specific
          run id.
        </p>
        <div className="action-row">
          <Link className="button primary" href="/">
            Back to landing page
          </Link>
          <Link className="button subtle" href="/run">
            Open latest/default run
          </Link>
          <a className="button subtle" href={`${demoApiBaseUrl}/runs/${params.runId}`}>
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
