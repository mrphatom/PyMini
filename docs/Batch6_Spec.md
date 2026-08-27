# Batch 6 Specification: Deterministic Decision Tables and Stable Action Plans

## Objective

PyMini should provide a small, deterministic rule-execution layer for Web3 scripts. The first slice targets the existing PyMini/Solana developer and must preserve the current language syntax, Batch 1–5 behavior, and Rust/PyO3 boundary. Success means a script can evaluate ordered decision rules and produce a reproducible action-plan identifier without using wall-clock time, randomness, network access, or private-key material.

## Assumptions

The primary user is a Web3 developer writing oracle and escrow decision scripts. The first release remains Python-interpreted and does not modify `pymini_core/`; Rust-backed state access stays behind the existing functions. Existing `clock()` and timestamped `log_audit()` behavior are retained for compatibility in this slice, but they remain explicitly tracked as determinism debt and must not be used by deterministic rule scripts.

## Feature contract

`decide(rules)` accepts a PyMini list of dictionaries. Each dictionary must contain `when` and `result` keys. Rules are examined in list order. The first truthy `when` returns its `result`; if no rule matches, `decide()` returns the existing PyMini `null` singleton. Invalid inputs raise a runtime error that can be caught by Batch 1 `try`/`catch`.

`canonical(value)` returns a deterministic string representation. Primitive values, lists, dictionaries, and `null` are supported. Dictionary keys are emitted in sorted order, while list order is preserved. Unsupported callable or byte values raise a runtime error instead of producing unstable output.

`stable_hash(value)` returns the lowercase SHA-256 hexadecimal digest of `canonical(value)`. It is deterministic across processes and suitable for idempotency keys and audit references. It does not use Python's process-randomized `hash()`.

`plan_action(kind, payload)` returns a dictionary containing `kind`, `payload`, and `id`, where `id` is `stable_hash({"kind": kind, "payload": payload})`. It creates data only; it does not contact Solana, read credentials, sign, or send a transaction.

## Commands

Build and run the interpreter:

```bash
python3 pymini.py examples/batch6_decisions.pymin
```

Run the focused tests:

```bash
python3 tests/test_batch6.py
```

Run the full regression suite:

```bash
python3 tests/test_all_batches.py
```

## Project structure

`pymini.py` remains the interpreter and built-in registry. `tests/` contains deterministic subprocess tests. `examples/batch6_decisions.pymin` demonstrates decision tables and stable action plans. `pymini_core/` remains unchanged in Batch 6 Slice 1.

## Code style

Built-ins are small `PyMiniCallable` classes with explicit arity checks and descriptive runtime errors. Canonicalization is implemented as a pure helper so both `canonical()` and `stable_hash()` share exactly the same representation.

```pymin
let decision = decide([
    {"when": true, "result": "RELEASE"},
    {"when": true, "result": "ESCALATE"}
]);
let action = plan_action(decision, {"escrow": "escrow_1"});
print(action["id"]);
```

## Testing strategy

Focused tests execute representative PyMini programs in subprocesses and compare stdout exactly. The suite covers first-match ordering, empty and invalid rule tables, nested canonical values, cross-process stable hashes, deterministic action-plan IDs, and the existing Batch 1–5 regression scripts. No network or Rust extension behavior is required for the new pure functions.

## Boundaries

Always validate input shapes, preserve the PyMini null singleton, sort dictionary keys during canonicalization, and run the existing regression suite before committing. Ask first before changing the Rust extension, adding network calls, changing transaction authorization, or altering existing `clock()`/`log_audit()` semantics. Never use Python's randomized `hash()`, embed secrets, send transactions from these helpers, or silently coerce malformed rule data.

## Success criteria

A valid ordered rule table returns its first matching result. No matching rule returns PyMini `null`. Canonical output and SHA-256 IDs are identical across two fresh interpreter processes. Action plans are plain data with no side effects. Invalid inputs fail with catchable runtime errors. Batch 1–5 tests remain green, `pymini_core/` has no changes, and README documentation explains all four new built-ins.

## Not in this slice

This slice does not add new grammar, pattern-matching syntax, modules, async execution, persistence, network calls, automatic transaction sending, or changes to Rust. Those are separate proposals that require their own contracts and tests.
