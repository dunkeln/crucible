from answer_verifier import accepted


passing = {"answer": "17 units", "evidence": ["The contract total is 17 units."]}
failing = {"answer": "17 units", "evidence": ["The prose implies about seventeen."]}
missing = {"answer": "17 units"}

assert accepted(passing)
assert not accepted(failing)
assert not accepted(missing)
