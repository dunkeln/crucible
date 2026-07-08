import Link from "next/link";
import { demoApiBaseUrl, fetchRuns } from "../lib/demo-api";

export default async function LandingPage() {
  let runs: Awaited<ReturnType<typeof fetchRuns>> = [];

  try {
    runs = await fetchRuns();
  } catch {
    runs = [];
  }

  return (
    <main className="page-shell">
      <section className="hero">
        <span className="eyebrow">Crucible</span>
        <h1>A model can try a thousand times a second. A person can only check so many.</h1>
        <p>
          Crucible does the checking the same way every time, so the pile of tries
          turns into lessons worth keeping without a person grading each answer by
          hand.
        </p>
        <div className="action-row">
          <Link className="button primary" href="/run">
            See one run
          </Link>
          <a className="button subtle" href={`${demoApiBaseUrl}/runs/demo`}>
            Open the raw data
          </a>
        </div>
      </section>

      <section className="status-strip">
        <article className="card">
          <div className="label">The slow part</div>
          <h3>The person is the ceiling</h3>
          <p>
            The model can try a million times. But if one person has to look at
            every answer, the pile only shrinks as fast as one tired human.
          </p>
        </article>

        <article className="card">
          <div className="label">The move</div>
          <h3>Repeat the boring part</h3>
          <p>
            The model tries. A checker says right or wrong. A score says how good.
            A fix shows the better way. Each try is saved as a small lesson.
          </p>
        </article>

        <article className="card">
          <div className="label">Why trust it</div>
          <h3>A test, not a hunch</h3>
          <p>
            Every score comes from a check written before the model ever runs. The
            answer passes or it does not, so a failed try is proof, not trash.
          </p>
        </article>
      </section>

      <section className="section-block">
        <h2 className="section-title">Runs the machine already made</h2>
        <p className="section-copy">
          Each one is a full loop: a task, a try, a check, a score, a fix, and a
          saved lesson. Open one and read it top to bottom.
        </p>
        {runs.length > 0 ? (
          <div className="route-list" style={{ marginTop: 14 }}>
            {runs.slice(0, 10).map((run) => (
              <Link className="route-card" href={`/run/${run.run_id}`} key={run.run_id}>
                <strong>{run.run_id}</strong>
                <span>
                  task: {run.task_id} | reward: {run.reward} | passed:{" "}
                  {String(run.passed)}
                </span>
              </Link>
            ))}
          </div>
        ) : (
          <ul className="note-list">
            <li>No runs yet.</li>
          </ul>
        )}
      </section>
    </main>
  );
}
