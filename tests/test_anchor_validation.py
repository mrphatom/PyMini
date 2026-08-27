import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pymini

ROOT = Path(__file__).resolve().parents[1]
PYMINI = ROOT / "pymini.py"
PROGRAM = "52yt1gCbPeiKP4JYjUVKmMJSgBMMcUx8xRGqozMKX2Mu"
SYSTEM = "11111111111111111111111111111111"
RELEASE_DISCRIMINATOR = "[24, 34, 191, 86, 145, 160, 183, 233]"


def run_program(source):
    with tempfile.NamedTemporaryFile("w", suffix=".pymin", delete=False) as handle:
        handle.write(source)
        path = handle.name
    try:
        return subprocess.run(
            [sys.executable, str(PYMINI), path],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        os.unlink(path)


def test_schema_is_derived_from_idl():
    result = run_program('''
    let schema = anchor_schema("initialize_job");
    print(schema["instruction"]);
    print(schema["args"][0]["name"]);
    print(schema["args"][0]["type"]);
    print(schema["accounts"][0]["name"]);
    ''')
    assert result.stderr == ""
    assert result.stdout == "initialize_job\njob_id\nstring\nclient\n", result.stdout


def test_valid_full_action_and_legacy_action_pass():
    result = run_program(f'''
    let full = {{
        "instruction": "initialize_job",
        "program_id": "{PROGRAM}",
        "accounts": {{
            "client": "{SYSTEM}",
            "freelancer": "{SYSTEM}",
            "oracle": "{SYSTEM}",
            "escrow_account": "{SYSTEM}",
            "vault_account": "{SYSTEM}",
            "system_program": "{SYSTEM}"
        }},
        "args": {{"job_id": "job-1", "amount": 100, "duration_seconds": 3600}}
    }};
    print(anchor_validate_action(full));
    let legacy = {{
        "type": "release_payment",
        "program_id": "{PROGRAM}",
        "escrow_address": "{SYSTEM}",
        "authority": "{SYSTEM}",
        "data": {RELEASE_DISCRIMINATOR}
    }};
    print(anchor_validate_action(legacy));
    ''')
    assert result.stderr == ""
    assert result.stdout == "true\ntrue\n", result.stdout


def test_anchor_plan_action_embeds_schema_and_id():
    result = run_program(f'''
    let action = anchor_plan_action(
        "initialize_job",
        "{PROGRAM}",
        {{
            "client": "{SYSTEM}",
            "freelancer": "{SYSTEM}",
            "oracle": "{SYSTEM}",
            "escrow_account": "{SYSTEM}",
            "vault_account": "{SYSTEM}",
            "system_program": "{SYSTEM}"
        }},
        {{"job_id": "job-1", "amount": 100, "duration_seconds": 3600}}
    );
    print(action["schema"]["instruction"]);
    print(action["schema"]["args"][1]["type"]);
    print(action["id"] == stable_hash({{
        "instruction": "initialize_job",
        "program_id": "{PROGRAM}",
        "accounts": action["accounts"],
        "args": action["args"]
    }}));
    ''')
    assert result.stderr == ""
    assert result.stdout == "initialize_job\nu64\ntrue\n", result.stdout


def test_idl_program_id_is_enforced():
    result = run_program(f'''
    try {{
        anchor_validate_action({{
            "instruction": "release_payment",
            "program_id": "{SYSTEM}",
            "accounts": {{
                "authority": "{SYSTEM}",
                "freelancer": "{SYSTEM}",
                "client": "{SYSTEM}",
                "escrow_account": "{SYSTEM}",
                "vault_account": "{SYSTEM}",
                "system_program": "{SYSTEM}"
            }},
            "args": {{}}
        }});
    }} catch (err) {{
        print("program-caught");
    }}
    ''')
    assert result.stderr == ""
    assert result.stdout == "program-caught\n", result.stdout


def test_validation_gate_runs_before_rust_call():
    calls = []

    def fake_rust_action(instruction):
        calls.append(instruction)
        return "sent"

    gate = pymini.ValidatedRustFunction(fake_rust_action, 1, 0)
    try:
        gate.call(None, [{"type": "release_payment", "program_id": SYSTEM}])
    except Exception as error:
        assert any(fragment in str(error) for fragment in ("missing", "valid", "match"))
    else:
        raise AssertionError("invalid action was accepted")
    assert calls == []


def test_invalid_actions_are_catchable():
    result = run_program(f'''
    try {{
        anchor_validate_action({{"instruction": "unknown", "program_id": "{PROGRAM}"}});
    }} catch (err) {{
        print("unknown-caught");
    }}
    try {{
        anchor_validate_action({{
            "instruction": "initialize_job",
            "program_id": "{PROGRAM}",
            "accounts": {{}},
            "args": {{"job_id": "job-1", "amount": -1, "duration_seconds": 3600}}
        }});
    }} catch (err) {{
        print("type-caught");
    }}
    try {{
        anchor_validate_action({{
            "type": "release_payment",
            "program_id": "{PROGRAM}",
            "escrow_address": "{SYSTEM}",
            "authority": "{SYSTEM}",
            "data": [0, 0, 0, 0, 0, 0, 0, 0]
        }});
    }} catch (err) {{
        print("discriminator-caught");
    }}
    ''')
    assert result.stderr == ""
    assert result.stdout == "unknown-caught\ntype-caught\ndiscriminator-caught\n", result.stdout


if __name__ == "__main__":
    for test in (
        test_schema_is_derived_from_idl,
        test_valid_full_action_and_legacy_action_pass,
        test_anchor_plan_action_embeds_schema_and_id,
        test_idl_program_id_is_enforced,
        test_validation_gate_runs_before_rust_call,
        test_invalid_actions_are_catchable,
    ):
        test()
        print(f"PASS: {test.__name__}")
