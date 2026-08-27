# PyMini Batch 6 Delivery Report

## What shipped

PyMini now has a deterministic rule-execution slice designed for Web3 oracle and escrow workflows. The new `decide(rules)` builtin evaluates an ordered list of rule dictionaries and returns the first matching `result`, or PyMini `null` when no rule matches. Malformed rules fail explicitly and remain catchable through the existing `try`/`catch` mechanism.

The new `canonical(value)` builtin produces a stable representation for supported primitives, lists, dictionaries, and null values. Dictionary keys are sorted and list order is preserved. `stable_hash(value)` computes a reproducible SHA-256 identifier from that canonical representation. `plan_action(kind, payload)` creates a side-effect-free action dictionary containing `kind`, `payload`, and a stable `id`, making it suitable for idempotency keys, audit references, and downstream transaction planning without signing or sending anything.

A small robustness fix also prevents the local `pymini_core/` source directory from being mistaken for a loaded Rust extension. When the compiled extension is not installed, ordinary PyMini programs continue to run and Rust-backed builtins are simply unavailable instead of crashing interpreter startup.

## Files changed

| Path | Purpose |
|---|---|
| `pymini.py` | Added the four deterministic builtins and validated optional Rust-core detection. |
| `examples/batch6_decisions.pymin` | Demonstrates first-match oracle decisions, explanations, canonical payloads, and action IDs. |
| `tests/test_batch6.py` | Focused tests for rule ordering, invalid rules, canonicalization, stable hashes, and fresh-process reproducibility. |
| `tests/test_all_batches.py` | Full regression harness covering Batch 1 through Batch 6 behavior. |
| `docs/Batch6_Spec.md` | Living specification, boundaries, commands, and success criteria. |
| `README.md` | Documents the new language capabilities and test commands. |

`pymini_core/` was not modified in this slice.

## Verification evidence

The focused suite passed:

```text
PASS: test_decide_first_match_and_null_fallback
PASS: test_canonical_and_stable_hash_are_order_independent
PASS: test_stable_hash_matches_in_a_fresh_process
```

The full regression suite passed:

```text
PASS: comments
PASS: null
PASS: try-catch
PASS: c-style-for
PASS: explain
PASS: for-in
PASS: determinism-guardrails
PASS: dict-read-write
PASS: dict-size
PASS: block-ambiguity
PASS: nested-dict-list
PASS: decision-table
PASS: action-plan
ALL BATCH 1–6 TESTS PASSED
```

The example produced a `RELEASE` decision, a canonical payload with sorted keys, and the same stable action ID for the same payload. Python bytecode compilation and `git diff --check` also passed.

## Git status

The change was committed and pushed to `origin/main`:

```text
fd600ef (HEAD -> main, origin/main, origin/HEAD) feat: add deterministic decision tables and action plans
7f8e332 Batch 5: Integrate Anchor client, typed escrow fetch, and guarded transactions
48ff876 Batch 3: Implement Native Dict Literals and Indexed Assignment
5c0d372 Batch 2: Implement explain(), for-in loop, and Determinism Guardrails
979f23e Batch 1: Implement Comments, Null, Try/Catch, and For-loops
```

The final working tree was clean and up to date with `origin/main`.

## Honest limitations and next directions

This slice deliberately does not add new grammar, modules, asynchronous execution, persistence, network behavior, or Rust changes. The existing `clock()` and timestamped `log_audit()` implementations remain compatibility debt because they are nondeterministic; they were not silently changed in this release. A subsequent slice should decide whether to preserve them as explicitly nondeterministic legacy helpers or replace them with injected execution metadata.

The strongest next candidates are a declarative `match`/pattern layer over dictionaries, typed action schemas derived from the Anchor IDL, and a dry-run execution journal that records inputs, decisions, explanations, and planned actions without performing external side effects. Each should receive a separate specification and focused regression slice.
