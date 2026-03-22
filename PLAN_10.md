# Plan: Verify `fib(n)` behavior and script output for issue #10

## Overview

This task proves the repository exposes a Python Fibonacci function and script entry point that satisfy issue #10. The work is intentionally scoped to one slice because the requested behavior is small and already isolated in `fib.py` and `tests/test_fib.py`. The contract focuses on committed behavioral evidence fetched from canonical slice artifacts at the Phase 4 submission commit SHA.

## Diagnosis Summary

The task is already well scoped, so this plan runs in PLAN mode rather than INVESTIGATE mode. `fib.py` defines `fib(n)` and a script entry point that prints `fib(10)` (`fib.py:1-11`), and `tests/test_fib.py` checks `fib(0)`, `fib(1)`, `fib(2)`, `fib(10)`, and `fib(20)` (`tests/test_fib.py:1-21`). The slice below proves those behaviors with committed logs fetched from `evidence/slice1/` at the Phase 4 submission commit SHA.

## Slices

---

### Slice 1: Prove Fibonacci outputs and script entry point

**Objective:** Prove that `fib(n)` returns the expected Fibonacci numbers for the repository's covered inputs and that running `fib.py` prints `55` for `fib(10)`.

#### Acceptance Criteria

- AC-1: `python3 -m pytest tests/test_fib.py -vv` exits 0 and the log fetched from `evidence/slice1/test_run.log` at the Phase 4 submission commit SHA contains `tests/test_fib.py::test_fib_0 PASSED`, `tests/test_fib.py::test_fib_1 PASSED`, `tests/test_fib.py::test_fib_2 PASSED`, `tests/test_fib.py::test_fib_10 PASSED`, and `tests/test_fib.py::test_fib_20 PASSED` — verified by `evidence/slice1/test_run.log` at the submission commit SHA
- AC-2: `python3 fib.py` exits 0 and the log fetched from `evidence/slice1/fib_run.log` at the Phase 4 submission commit SHA contains exactly `55` as its only stdout line — verified by `evidence/slice1/fib_run.log` at the submission commit SHA

## Constraints

- Python: python3
- Runner: `python3 -m pytest`
- Isolation flags: none
- No unauthorized package installations
- No pkill, no rm -rf, no python main.py

## Out of Scope

- Adding command-line arguments or interactive input to `fib.py`
- Refactoring the repository into a package layout
- Expanding coverage beyond the existing repository cases in `tests/test_fib.py`
- Changing the Fibonacci definition away from the standard `0, 1, 1, 2, 3, ...` sequence
