from ingress_normalize import normalize_records


raw = [
    {" Record ID ": " 42 ", " Question ": " 2 + 2? ", " Gold ": " 4 ", " Source Tag ": " eval "},
    {"id": "43", "prompt": "Capital?", "answer": " Paris ", "Extra Field": " kept "},
]

expected = [
    {"id": "42", "prompt": "2 + 2?", "answer": "4", "source_tag": "eval"},
    {"id": "43", "prompt": "Capital?", "answer": "Paris", "extra_field": "kept"},
]

assert normalize_records(raw) == expected
