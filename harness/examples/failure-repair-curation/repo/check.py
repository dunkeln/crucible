from pathlib import Path


main_py = Path("main.py").read_text()
failing_attempt = Path("failing_attempt.patch").read_text()
failing_result = Path("failing_verifier.txt").read_text()
teacher_note = Path("teacher_note.md").read_text()

assert "from harness.main import main" in main_py
assert "from demo_surface import main" not in main_py
assert "demo_surface.py" in failing_attempt
assert "exit_code: 1" in failing_result
assert "symptom shim" in teacher_note
assert "root cause" in teacher_note
assert "harness.main" in teacher_note
