# Batch 7 Specification: Anchor-IDL Action Schemas and Validation

## Objective

PyMini should derive Solana transaction action schemas from the bundled Mappers Anchor IDL and reject malformed actions before they reach the Rust transaction boundary. The slice must preserve existing PyMini syntax, legacy Rust action dictionaries, Rust send guard rails, deterministic planning behavior, and the rule that no real transaction is sent without explicit authorization.

## Source and scope

`idl.json` at the repository root is the local source of truth. This slice supports the four bundled instructions and does not fetch live IDLs, add syntax, change `pymini_core/`, add dependencies, or infer schemas from network data.

## Public contract

`anchor_schema(instruction)` returns a dictionary containing the bundled `program_id`, instruction name, discriminator, argument names and IDL type descriptors, and account names with `signer` and `writable` metadata.

A full declarative action has this shape:

```pymin
{
    "instruction": "initialize_job",
    "program_id": "<bundled program id>",
    "accounts": {"account_name": "<base58 public key>"},
    "args": {"argument_name": "value"}
}
```

`anchor_validate_action(action)` accepts full actions and the existing legacy Rust shape. Full actions require exact account and argument key sets, the bundled program ID, valid base58 32-byte public keys, and values matching the IDL type descriptors. Supported descriptors include strings, booleans, public keys, fixed-width signed and unsigned integers, options, vectors, and fixed-length arrays. Legacy actions retain their existing `type`, `program_id`, `escrow_address`, `authority`, and discriminator-list fields; they are validated against the corresponding IDL instruction and remain compatible with current Rust builders.

`anchor_plan_action(instruction, program_id, accounts, args)` validates a full action, includes its derived schema, and adds a stable SHA-256 ID based on the canonical action identity. Planning is pure: it performs no RPC, signing, keypair access, or transaction submission.

The existing `anchor_simulate_tx()` and `anchor_send_tx()` evaluator bindings validate their action argument before calling Rust. Rust-generated release and cancel actions are validated after construction. Rust's existing devnet-only RPC check, `PYMINI_ALLOW_SEND=1` process gate, environment-variable keypair-path convention, and signer equality check remain authoritative.

## Errors and safety boundaries

Unknown instructions, wrong program IDs, missing or unexpected keys, malformed public keys, invalid scalar or nested values, and discriminator mismatches raise ordinary catchable PyMini runtime errors. Validation failure must happen before the wrapped Rust callable is invoked. No helper in this slice can send a real transaction or bypass Rust authorization checks.

## Commands

```bash
python3 tests/test_anchor_validation.py
python3 -m py_compile pymini.py tests/test_anchor_validation.py tests/test_batch6.py tests/test_all_batches.py
python3 tests/test_batch6.py
python3 tests/test_all_batches.py
```

## Testing strategy

Focused tests cover schema derivation from the bundled IDL, valid full and legacy actions, stable planning output, program-ID enforcement, invalid scalar/discriminator cases, catchability, and a pre-Rust gate proving an invalid payload does not invoke the wrapped callable. Existing Batch 1–6 tests remain unchanged and must remain green. No network, keypair, or live transaction test is required or permitted for this slice.

## Boundaries

Always load the local IDL deterministically, validate exact shapes and ranges, keep secrets out of source and Git, and run focused plus full regression tests before committing. Ask first before modifying Rust, changing transaction authorization, adding network behavior, or performing an actual send. Never silently coerce malformed action data or treat a plan as permission to submit.

## Success criteria

The focused Anchor suite passes; Python compilation and Batch 6/full regression suites pass; invalid payloads are rejected before Rust invocation; existing legacy action shapes validate; `pymini_core/` is unchanged; diagnostic-only utilities are absent; README documents the public APIs and safety boundary; and the focused changes are committed and pushed to `origin/main`.

## Files

`pymini.py` contains the pure schema derivation, recursive type validation, public built-ins, and Rust-boundary wrappers. `tests/test_anchor_validation.py` contains focused tests. `README.md` documents usage. This specification records the compatibility and safety contract.
