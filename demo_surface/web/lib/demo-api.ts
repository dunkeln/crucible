export type DemoRun = {
  task: string;
  attempt: string;
  verifier_result: string;
  reward: string;
  teacher_repair: string;
  curated_row: string;
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

export async function fetchHealth(): Promise<{ status: string }> {
  const response = await fetch(`${demoApiBaseUrl}/health`, {
    cache: "no-store"
  });

  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }

  return (await response.json()) as { status: string };
}
