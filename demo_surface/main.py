import json
import os
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import urlopen


@dataclass(frozen=True)
class DemoRun:
    task: str
    attempt: str
    verifier_result: str
    reward: str
    teacher_repair: str
    curated_row: str


def render_section(title: str, body: str) -> str:
    border = "=" * len(title)
    return f"{title}\n{border}\n{body}"


DEFAULT_API_URL = "http://127.0.0.1:8000/runs/demo"


def fetch_demo_run(api_url: str) -> DemoRun:
    with urlopen(api_url) as response:
        payload = json.loads(response.read().decode("utf-8"))

    return DemoRun(
        task=payload["task"],
        attempt=payload["attempt"],
        verifier_result=payload["verifier_result"],
        reward=payload["reward"],
        teacher_repair=payload["teacher_repair"],
        curated_row=payload["curated_row"],
    )


def render_demo(run: DemoRun) -> str:
    sections = [
        render_section("Crucible Demo Surface", "One sample run rendered from the local API."),
        render_section("Task", run.task),
        render_section("Attempt", run.attempt),
        render_section("Verifier Result", run.verifier_result),
        render_section("Reward", run.reward),
        render_section("Teacher Repair", run.teacher_repair),
        render_section("Curated Row Export", run.curated_row),
    ]
    return "\n\n".join(sections)


def main() -> None:
    api_url = os.environ.get("DEMO_SURFACE_API_URL", DEFAULT_API_URL)
    try:
        print(render_demo(fetch_demo_run(api_url)))
    except URLError as error:
        raise SystemExit(
            "Could not reach the demo surface API.\n"
            f"Start it with `python -m demo_surface.api` and retry.\n"
            f"API URL: {api_url}\n"
            f"Error: {error.reason}"
        )


if __name__ == "__main__":
    main()
