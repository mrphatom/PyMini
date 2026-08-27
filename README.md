# PyMini

PyMini is a lightweight, interpreted programming language implemented in Python. It is designed to be simple, readable, and expressive, featuring a syntax inspired by modern scripting languages.

## Features

- **Dynamic Typing:** No need to declare variable types.
- **First-Class Functions:** Define and pass functions with ease.
- **Control Flow:** Supports `if-else` conditionals, `while` loops, and logical operators (`and`, `or`).
- **Arithmetic:** Full support for `+`, `-`, `*`, `/`, and `%` (modulo).
- **Built-in Functions:** Native functions like `clock()`, `len()`, and Web3 helpers.
- **Rust Core (PyO3):** High-performance Solana-facing logic implemented in Rust.
- **Web3 Features:** Direct Solana RPC integration and Borsh deserialization.
- **Anchor Integration:** IDL-driven `GigEscrow` fetching, instruction construction, simulation, and gated devnet sending.
- **Assertions and Audit Logs:** Catchable `assert()` checks and timestamped `log_audit()` persistence.
- **Lexical Scoping:** Proper variable management within blocks and functions.
- **Clean Syntax:** Minimalist design with a focus on clarity.
- **Comments:** Support for `#` line comments.
- **Null Safety:** Explicit `null` literal and `is_null()` check.
- **Error Handling:** Robust `try-catch` blocks for runtime safety.
- **Looping:** C-style `for` loops and `for...in` iterator loops.
- **Dictionaries:** Native dict literals `{"key": value}` with indexing and assignment.
- **Traceability:** `explain()` and `get_explanations()` for rule execution transparency.
- **Determinism:** Strict-mode guardrails blocking `random()` and `now()`.
- **Decision Tables:** Ordered `decide()` rules for explicit first-match oracle logic.
- **Reproducible Plans:** `canonical()`, `stable_hash()`, and `plan_action()` for stable, side-effect-free action identities.

## Installation

Ensure you have Python 3.x and Rust installed on your system. 

1. Clone the repository:
```bash
git clone https://github.com/mrphatom/PyMini.git
cd PyMini
```

2. Build and install the Rust core:
```bash
cd pymini_core
maturin build --release
pip install target/wheels/*.whl
cd ..
```

## Usage

### Running a Script

You can execute PyMini source files (typically using the `.pymin` extension) by passing the file path to the interpreter:

```bash
python3 pymini.py examples/hello.pymin
```

### Interactive REPL

For quick testing and experimentation, you can launch the PyMini REPL:

```bash
python3 pymini.py
```

## Language Syntax

### Variables
Use the `let` keyword to declare variables:
```pymin
let x = 10;
let message = "Hello, World!";
```

### Functions
Functions are defined using the `func` keyword:
```pymin
func add(a, b) {
    return a + b;
}

print(add(5, 7)); // Outputs: 12
```

### Web3 (Solana)
PyMini supports Solana operations via its Rust core:
```pymin
let rpc = "https://api.mainnet-beta.solana.com";
let addr = "11111111111111111111111111111111";
let balance = solana_get_balance(rpc, addr);
print(balance);
```

### Batch 5 Anchor Integration

The Rust extension bundles the Mappers Anchor IDL and exposes typed `GigEscrow` fetching through `anchor-client` and Borsh-compatible decoding:

```pymin
let rpc = "https://api.devnet.solana.com";
let program = "52yt1gCbPeiKP4JYjUVKmMJSgBMMcUx8xRGqozMKX2Mu";
let escrow = anchor_fetch_account(rpc, program, escrow_address, "GigEscrow");
print(escrow["status"]);
print(escrow["amount"]);
```

Instruction builders return dictionaries and do not send transactions:

```pymin
let ix = anchor_build_release_ix(program, escrow_address, oracle_pubkey);
let simulation = anchor_simulate_tx(rpc, ix);
print(simulation["success"]);
```

`assert(condition, message)` raises a catchable runtime error when the condition is false. `log_audit(path, message)` appends a timestamped audit entry:

```pymin
assert(escrow["status"] == "Pending", "cannot release a non-pending job");
log_audit("audit.log", "escrow checked");
```

## Safety

`anchor_send_tx(rpc, instruction, keypair_env_var)` is deliberately restricted. The third argument is only the **name** of an environment variable; keypair material must remain outside PyMini source files. The Rust layer requires the RPC URL to contain `devnet`, requires the process-level environment variable `PYMINI_ALLOW_SEND=1`, and reads the keypair path from the named environment variable. Mainnet URLs are rejected even when the enable flag is present. These checks are implemented in Rust and cannot be bypassed by a `.pymin` script.

The repository does not include a private key or a live escrow fixture. The `examples/escrow_status.pymin` example uses a safe placeholder address and reports the fetch error until a real devnet `GigEscrow` PDA is supplied.

### Batch 1 Extensions

#### Comments
```pymin
# This is a comment
let x = 10; # Trailing comment
```

#### Null
```pymin
let x = null;
if (is_null(x)) {
    print("x is null");
}
```

#### Try/Catch
```pymin
try {
    let result = 10 / 0;
} catch (err) {
    print("Caught error: ");
    print(err);
}
```

#### For-loop
```pymin
# C-style
for (let i = 0; i < 5; i = i + 1) {
    print(i);
}

# Iterator-style
let items = [10, 20, 30];
for item in items {
    print(item);
}
```

#### Dictionaries
```pymin
let d = {"a": 1, "b": 2};
print(d["a"]);    # Read
d["c"] = 3;       # Write
print(dict_size(d)); # 3
```

### Batch 2 Extensions

#### explain() & get_explanations()
```pymin
explain("starting validation");
# ... logic ...
let trace = get_explanations();
print(trace[0]); # "starting validation"
```

#### Determinism Guardrails
PyMini enforces strict determinism. Calling non-deterministic functions will raise a runtime error:
```pymin
try {
    random();
} catch (err) {
    print(err); # "random() is blocked in strict mode."
}
```

### Control Flow
```pymin
if (x > 5) {
    print("Greater");
} else {
    print("Smaller or equal");
}

let i = 0;
while (i < 3) {
    print(i);
    i = i + 1;
}
```

### Batch 6 Extensions

Batch 6 adds a deterministic rule layer for Web3 decisions. `decide(rules)` evaluates a list of dictionaries in order and returns the first matching rule's `result`; when no rule matches, it returns PyMini `null`. Each rule must contain `when` and `result`, so malformed decision tables fail loudly and remain catchable through `try`/`catch`.

```pymin
let decision = decide([
    {"when": gemini_approved, "result": "RELEASE"},
    {"when": both_rejected, "result": "REFUND"},
    {"when": true, "result": "ESCALATE"}
]);
```

`canonical(value)` returns a stable representation of supported primitive, list, dictionary, and null values. Dictionary keys are sorted while list order is preserved. `stable_hash(value)` returns a SHA-256 identifier of that canonical representation. `plan_action(kind, payload)` creates a plain action dictionary with `kind`, `payload`, and a reproducible `id`; it performs no network calls, signing, credential access, or transaction submission.

```pymin
let payload = {"escrow": "escrow_1", "decision": decision};
let action = plan_action(decision, payload);
print(action["id"]);
```

### Anchor-IDL Action Schemas and Validation

The bundled `idl.json` is now used as the local source of truth for transaction action validation. `anchor_schema(instruction)` exposes the instruction discriminator, argument names and IDL types, account names, signer/writable metadata, and the bundled program ID.

```pymin
let schema = anchor_schema("initialize_job");
print(schema["args"][0]["name"]); # job_id
print(schema["args"][0]["type"]); # string
```

`anchor_validate_action(action)` validates both the new full action shape and the existing Rust-generated legacy instruction shape. Full actions contain `instruction`, `program_id`, `accounts`, and `args`. Validation rejects unknown instructions, wrong program IDs, missing or unexpected accounts and arguments, malformed public keys, invalid integer ranges, unsupported types, and mismatched instruction discriminators. Errors are catchable with `try`/`catch`.

`anchor_plan_action(instruction, program_id, accounts, args)` validates a full action, embeds its IDL-derived schema, and returns a stable action ID. It is deliberately side-effect-free: it does not access credentials, call RPC, sign, or submit transactions. Existing `anchor_simulate_tx()` and `anchor_send_tx()` calls validate their action dictionaries before crossing into Rust, while Rust's devnet and authorization guard rails remain active.

```pymin
let action = anchor_plan_action(
    "initialize_job",
    "52yt1gCbPeiKP4JYjUVKmMJSgBMMcUx8xRGqozMKX2Mu",
    {
        "client": "11111111111111111111111111111111",
        "freelancer": "11111111111111111111111111111111",
        "oracle": "11111111111111111111111111111111",
        "escrow_account": "11111111111111111111111111111111",
        "vault_account": "11111111111111111111111111111111",
        "system_program": "11111111111111111111111111111111"
    },
    {"job_id": "job-1", "amount": 100, "duration_seconds": 3600}
);
print(action["id"]);
```

The focused and full regression suites are available under `tests/`:

```bash
python3 tests/test_anchor_validation.py
python3 tests/test_batch6.py
python3 tests/test_all_batches.py
```

## Project Structure

- `pymini.py`: The core interpreter containing the lexer, parser, tree-walk evaluator, and built-ins.
- `pymini_core/`: The PyO3 Rust extension containing Solana RPC, Anchor-client, Borsh decoding, simulation, and guarded sending.
- `idl.json`: The bundled Mappers Anchor IDL used by the Rust extension.
- `examples/`: Sample PyMini programs, including `batch6_decisions.pymin`, `escrow_status.pymin`, `oracle_decision.pymin`, and `assert_audit.pymin`.
- `tests/`: Focused and full deterministic regression tests.
- `docs/`: Detailed language design and Batch 6 specification.

## References

- [Anchor Rust client documentation](https://www.anchor-lang.com/docs/clients/rust)
- [anchor-client 0.29 `Client` API](https://docs.rs/anchor-client/0.29.0/anchor_client/struct.Client.html)
- [anchor-client 0.29 `Program` API](https://docs.rs/anchor-client/0.29.0/anchor_client/struct.Program.html)
