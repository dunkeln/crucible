from __future__ import annotations

import json


ALIASES = {
    "id": "id",
    "record_id": "id",
    "question": "prompt",
    "prompt": "prompt",
    "gold": "answer",
    "answer": "answer",
}


def clean_key(value: str) -> str:
    return "_".join(value.strip().lower().split())


def clean_value(value: object) -> object:
    return value.strip() if isinstance(value, str) else value


def normalize_record(record: dict[str, object]) -> dict[str, object]:
    normalized: dict[str, object] = {}
    for key, value in record.items():
        clean = clean_key(key)
        normalized[ALIASES.get(clean, clean)] = clean_value(value)
    return normalized


def normalize_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    return [normalize_record(record) for record in records]


def demo() -> None:
    raw = [
        {" Record ID ": " 42 ", " Question ": " 2 + 2? ", " Gold ": " 4 ", " Source Tag ": " eval "},
        {"id": "43", "prompt": "Capital?", "answer": " Paris ", "Extra Field": " kept "},
    ]
    expected = [
        {"id": "42", "prompt": "2 + 2?", "answer": "4", "source_tag": "eval"},
        {"id": "43", "prompt": "Capital?", "answer": "Paris", "extra_field": "kept"},
    ]
    actual = normalize_records(raw)
    assert actual == expected
    print(json.dumps(actual, sort_keys=True))


if __name__ == "__main__":
    demo()
