ALIASES = {
    "id": "id",
    "record_id": "id",
    "question": "prompt",
    "prompt": "prompt",
    "gold": "answer",
    "answer": "answer",
}


def normalize_record(record):
    normalized = {}
    for key, value in record.items():
        clean = key.strip().lower()
        if clean in ALIASES:
            normalized[ALIASES[clean]] = value
    return normalized


def normalize_records(records):
    return [normalize_record(record) for record in records]
