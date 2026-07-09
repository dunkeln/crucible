from __future__ import annotations


SOURCE = "The contract total is 17 units. Delivery is due Friday."


def accepted(output: dict[str, object], source: str = SOURCE) -> bool:
    evidence = output.get("evidence")
    return (
        output.get("answer") == "17 units"
        and isinstance(evidence, list)
        and "The contract total is 17 units." in evidence
        and all(isinstance(item, str) and item in source for item in evidence)
    )


def demo() -> None:
    passing = {"answer": "17 units", "evidence": ["The contract total is 17 units."]}
    failing = {"answer": "17 units", "evidence": ["The prose implies about seventeen."]}
    assert accepted(passing)
    assert not accepted(failing)
    print("accepted=passing rejected=failing")


if __name__ == "__main__":
    demo()
