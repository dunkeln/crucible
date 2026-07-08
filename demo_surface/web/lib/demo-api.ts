export type DemoRun = {
  task: string;
  attempt: string;
  verifier_result: string;
  reward: string;
  teacher_repair: string;
  curated_row: string;
};

export type RunSummary = {
  run_id: string;
  task_id: string;
  created_at: string;
  passed: boolean;
  reward: number;
};

export const demoApiBaseUrl =
  process.env.NEXT_PUBLIC_DEMO_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function fetchDemoRun(): Promise<DemoRun> {
  const response = await fetch(`${demoApiBaseUrl}/runs/demo`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Demo API request failed with status ${response.status}`);
  }

  return (await response.json()) as DemoRun;
}

export async function fetchDemoRunById(runId: string): Promise<DemoRun> {
  const response = await fetch(`${demoApiBaseUrl}/runs/${runId}`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Run ${runId} request failed with status ${response.status}`);
  }

  return (await response.json()) as DemoRun;
}

export async function fetchRuns(): Promise<RunSummary[]> {
  const response = await fetch(`${demoApiBaseUrl}/runs`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Runs request failed with status ${response.status}`);
  }

  const payload = (await response.json()) as { runs: RunSummary[] };
  return payload.runs;
}

export async function fetchHealth(): Promise<{ status: string }> {
  const response = await fetch(`${demoApiBaseUrl}/health`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }

  return (await response.json()) as { status: string };
}
