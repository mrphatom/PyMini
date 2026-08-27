import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYMINI = ROOT / "pymini.py"


def run_program(source):
    with tempfile.NamedTemporaryFile("w", suffix=".pymin", delete=False) as handle:
        handle.write(source)
        path = handle.name
    try:
        result = subprocess.run(
            [sys.executable, str(PYMINI), path],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout, result.stderr
    finally:
        os.unlink(path)


def test_decide_first_match_and_null_fallback():
    stdout, _ = run_program(
        '''
        let rules = [
            {"when": false, "result": "NO"},
            {"when": true, "result": "RELEASE"},
            {"when": true, "result": "NEVER"}
        ];
        print(decide(rules));
        print(is_null(decide([])));
        try {
            decide([{"when": true}]);
        } catch (err) {
            print("invalid-rules-caught");
        }
        '''
    )
    assert stdout == "RELEASE\ntrue\ninvalid-rules-caught\n", stdout


def test_canonical_and_stable_hash_are_order_independent():
    stdout, _ = run_program(
        '''
        let value = {"z": [2, null], "a": true};
        print(canonical(value));
        print(stable_hash(value));
        let action = plan_action("RELEASE", value);
        print(action["kind"]);
        print(action["id"] == stable_hash({"kind": "RELEASE", "payload": value}));
        '''
    )
    lines = stdout.splitlines()
    assert lines[0] == '{"a": true, "z": [2, null]}', stdout
    assert lines[1] == hashlib.sha256(lines[0].encode()).hexdigest(), stdout
    assert lines[2:] == ["RELEASE", "true"], stdout


def test_stable_hash_matches_in_a_fresh_process():
    source = 'print(stable_hash({"b": 2, "a": 1}));'
    first, _ = run_program(source)
    second, _ = run_program(source)
    assert first == second


if __name__ == "__main__":
    for test in (
        test_decide_first_match_and_null_fallback,
        test_canonical_and_stable_hash_are_order_independent,
        test_stable_hash_matches_in_a_fresh_process,
    ):
        test()
        print(f"PASS: {test.__name__}")
