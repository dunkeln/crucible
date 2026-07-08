# Demo Surface Development Notes

The current demo surface is not connected to a live model, a training loop, or an RLVR runtime. Its job is narrower than that. It exists to prove that Crucible can show one complete evidence path from task to judgment in a way that is small, inspectable, and objectively runnable.

At this stage, the demo surface reads from a local HTTP API defined in [api.py](/D:/crucible/demo_surface/api.py). The API can serve either a sample payload from [data/demo_run.json](/D:/crucible/demo_surface/data/demo_run.json) or real harness outputs discovered under `data/runs/<run_id>/run.json`. The view layer in [main.py](/D:/crucible/demo_surface/main.py) fetches that payload before rendering it. The same API also serves a browser landing page at `/` and a human-readable run view at `/view`. That means the demo is now connected through an API boundary even though there is still no model inference yet and no verifier service owned by the demo itself. The program renders the fields that matter to Crucible: task, student attempt, verifier result, reward, teacher repair, and curated row export.

There is also a separate Next.js frontend in [web](/D:/crucible/demo_surface/web). That app talks to the same Python API and provides a browser-first landing page plus a run view without moving ownership of verification or training data into the frontend.

Because there is no model wired in yet, the honest answer to "what model are we using?" is: none. The current demo is a development scaffold. It is preparing the interface for future work, not claiming that model execution already exists. The same is true for the data. The demo is not consuming a real corpus yet. It is serving a single repository-local JSON example through the API so the team can verify the connection and the display before introducing more moving parts.

For a math-focused RLVR direction, the next smallest step is not choosing a bigger model or adding infrastructure. The next useful step is to define one or two concrete math rows in the same shape as the current example. A row should contain a short math task, a model attempt, an objective verifier result, a numeric reward, a teacher repair, and a compact export record. For example, a row might ask for the value of `2 + 3 * 4`, record an incorrect answer such as `20`, mark the verifier result as failure, assign a low reward, and include a repair that explains order of operations and the correct answer `14`.

That kind of row is useful because it keeps the verifier objective. Either the answer matches or it does not. This fits the Crucible philosophy well. It also gives the demo surface something closer to the eventual RLVR use case without forcing the repository to merge the harness, the corpus, and the UI too early.

In development terms, the current demo surface should be treated as a read-only presentation seam. It can display the loop and export a row shape, but it should not become the source of truth for verification logic or dataset structure. When model execution is added later, it should come from the agent harness seam. When reusable tasks and verifiers are added later, they should come from the task and verifier corpus seam. The demo surface can then read those artifacts and display them without taking ownership of them.

## How to test it

The current working check is intentionally small. From the repository root, start the API in one terminal:

```powershell
python -m demo_surface.api
```

Then, in a second terminal, run the viewer:

```powershell
python main.py
```

That command should fetch the sample run from `http://127.0.0.1:8000/runs/demo`, print the full demo surface, and exit with no error.

If you want to inspect it in a browser, open:

```text
http://127.0.0.1:8000/
```

The landing page should give you:

+ a browser-friendly run view at `/view`
+ the raw JSON endpoint at `/runs/demo`
+ a run index endpoint at `/runs`
+ a single run endpoint at `/runs/<run_id>`
+ redirect helpers at `/go?target=view` and `/go?target=json`
+ a health check at `/health`

If you want the Next.js landing page instead of the Python-rendered page, start it from [web](/D:/crucible/demo_surface/web):

```powershell
cd demo_surface\web
npm install
npm run dev
```

Then open:

```text
http://127.0.0.1:3000/
```

The Next.js landing page also links detected harness runs and opens them at `/run/<run_id>`.

The Next.js app expects the Python API to stay available at `http://127.0.0.1:8000`. You can override that with the `NEXT_PUBLIC_DEMO_API_BASE_URL` environment variable if needed.

You can also run the viewer directly from its own module path:

```powershell
python -m demo_surface.main
```

The API-backed viewer should show the same sections:

+ `Crucible Demo Surface`
+ `Task`
+ `Attempt`
+ `Verifier Result`
+ `Reward`
+ `Teacher Repair`
+ `Curated Row Export`

If the landing page loads, the redirect links work, and the CLI still prints the full run successfully, the demo surface API connection is working for its current purpose.
