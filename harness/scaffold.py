from __future__ import annotations

import json
from pathlib import Path


DEFAULT_MODEL = "Qwen/Qwen2.5-3B-Instruct"


def scaffold_math_rlvr(root: Path | str, package: str, model: str = DEFAULT_MODEL, force: bool = False) -> dict[str, object]:
    destination = Path(root)
    package_dir = destination / "src" / package
    files = {
        destination / "configs" / "qwen25_3b_math_rlvr.yaml": config_yaml(model),
        destination / "data" / "math_rlvr" / "train.jsonl": jsonl(
            [
                {"prompt": "What is 2 + 3 * 4?", "answer": "14"},
                {"prompt": "Solve for x: x + 7 = 12.", "answer": "5"},
            ]
        ),
        destination / "data" / "math_rlvr" / "eval.jsonl": jsonl(
            [
                {"prompt": "What is 9 - 4 / 2?", "answer": "7"},
                {"prompt": "Solve for x: 3x = 18.", "answer": "6"},
            ]
        ),
        package_dir / "__init__.py": "",
        package_dir / "cli.py": cli_py(package),
        package_dir / "math_reward.py": math_reward_py(),
        destination / "jobs" / "train_grpo_math.py": train_job_py(package),
        destination / "scripts" / "hf_download_model.sh": hf_download_sh(model),
        destination / "scripts" / "hf_upload_adapter.sh": hf_upload_sh(),
    }
    written = []
    for path, content in files.items():
        if path.exists() and not force:
            raise ValueError(f"refusing to overwrite existing file: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path.as_posix())
    return {
        "recipe": "math-rlvr",
        "model": model,
        "package": package,
        "root": destination.as_posix(),
        "files": written,
        "checks": [
            f"PYTHONPATH=src python -m {package}.cli check-reward",
            "PYTHONPATH=src python -m compileall -q src jobs main.py",
        ],
    }


def config_yaml(model: str) -> str:
    return f"""model: {model}
dataset:
  train: data/math_rlvr/train.jsonl
  eval: data/math_rlvr/eval.jsonl
reward:
  fn: math_reward.exact_answer_reward
training:
  method: grpo
  lora: true
  max_steps: 20
"""


def jsonl(rows: list[dict[str, str]]) -> str:
    return "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)


def cli_py(package: str) -> str:
    return f"""from __future__ import annotations

from {package}.math_reward import exact_answer_reward


def main() -> None:
    assert exact_answer_reward("14", "14") == 1.0
    assert exact_answer_reward("14", "15") == 0.0
    print("reward check passed")


if __name__ == "__main__":
    main()
"""


def math_reward_py() -> str:
    return """from __future__ import annotations


def normalize(value: str) -> str:
    return value.strip().lower().replace(",", "")


def exact_answer_reward(prediction: str, answer: str) -> float:
    return 1.0 if normalize(prediction) == normalize(answer) else 0.0
"""


def train_job_py(package: str) -> str:
    return f"""from __future__ import annotations

from pathlib import Path


def main() -> None:
    config = Path("configs/qwen25_3b_math_rlvr.yaml")
    if not config.exists():
        raise SystemExit(f"missing config: {{config}}")
    print("ponytail: placeholder GRPO job; install TRL/torch and replace when running real training")
    print(f"reward module: {package}.math_reward")


if __name__ == "__main__":
    main()
"""


def hf_download_sh(model: str) -> str:
    return f"""#!/usr/bin/env bash
set -euo pipefail

hf download {model}
"""


def hf_upload_sh() -> str:
    return """#!/usr/bin/env bash
set -euo pipefail

: "${HF_REPO_ID:?set HF_REPO_ID}"
: "${ADAPTER_DIR:=outputs/math_rlvr_adapter}"

hf upload "$HF_REPO_ID" "$ADAPTER_DIR"
"""
