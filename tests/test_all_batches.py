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


def check(name, source, expected):
    stdout, stderr = run_program(source)
    assert stderr == "", f"{name} wrote stderr: {stderr}"
    assert stdout == expected, f"{name} output:\n{stdout!r}\nexpected:\n{expected!r}"
    print(f"PASS: {name}")


check(
    "comments",
    "# full line comment\nlet x = 5; # trailing comment\nprint(x);\n",
    "5\n",
)
check(
    "null",
    '''
    let x = null;
    print(is_null(x));
    x = 5;
    print(is_null(x));
    print(null == null);
    print(null == 0);
    print(null == false);
    ''',
    "true\nfalse\ntrue\nfalse\nfalse\n",
)
check(
    "try-catch",
    '''
    try {
        let x = 10 / 0;
        print("unreachable");
    } catch (err) {
        print("caught");
    }
    ''',
    "caught\n",
)
check(
    "c-style-for",
    '''
    for (let i = 0; i < 3; i = i + 1) {
        print(i);
    }
    ''',
    "0\n1\n2\n",
)
check(
    "explain",
    '''
    explain("checking delivery status");
    explain("delivery confirmed");
    let trace = get_explanations();
    print(trace[0]);
    print(trace[1]);
    ''',
    "EXPLAIN: checking delivery status\nEXPLAIN: delivery confirmed\nchecking delivery status\ndelivery confirmed\n",
)
check(
    "for-in",
    '''
    let items = [10, 20, 30];
    for item in items {
        print(item);
    }
    let empty = [];
    for x in empty {
        print("should never print");
    }
    print("done");
    ''',
    "10\n20\n30\ndone\n",
)
check(
    "determinism-guardrails",
    '''
    try {
        random();
    } catch (err) {
        print("blocked-random");
    }
    try {
        now();
    } catch (err) {
        print("blocked-time");
    }
    ''',
    "blocked-random\nblocked-time\n",
)
check(
    "dict-read-write",
    '''
    let d = {"a": 1, "b": 2};
    print(d["a"]);
    print(d["b"]);
    d["c"] = 3;
    print(d["c"]);
    ''',
    "1\n2\n3\n",
)
check(
    "dict-size",
    '''
    let empty_d = {};
    print(dict_size(empty_d));
    let d2 = {"x": 10};
    print(dict_size(d2));
    ''',
    "0\n1\n",
)
check(
    "block-ambiguity",
    '''
    if (true) {
        print("block works");
    }
    let i = 0;
    while (i < 2) {
        print("loop works");
        i = i + 1;
    }
    func greet() {
        print("func works");
    }
    greet();
    ''',
    "block works\nloop works\nloop works\nfunc works\n",
)
check(
    "nested-dict-list",
    '''
    let record = {"name": "escrow_1", "amounts": [10, 20, 30]};
    print(record["name"]);
    print(record["amounts"][1]);
    ''',
    "escrow_1\n20\n",
)
check(
    "decision-table",
    '''
    let decision = decide([
        {"when": false, "result": "NO"},
        {"when": true, "result": "RELEASE"}
    ]);
    print(decision);
    print(is_null(decide([])));
    ''',
    "RELEASE\ntrue\n",
)
check(
    "action-plan",
    '''
    let payload = {"z": [2, null], "a": true};
    let plan = plan_action("RELEASE", payload);
    print(canonical(payload));
    print(plan["kind"]);
    print(plan["id"] == stable_hash({"kind": "RELEASE", "payload": payload}));
    ''',
    '{"a": true, "z": [2, null]}\nRELEASE\ntrue\n',
)
print("ALL BATCH 1–6 TESTS PASSED")
