# Plan: Implement `fib(n)` and CLI output for `fib(10)`

## Overview
This task makes the repository's Fibonacci example explicit and verifiable: a Python function `fib(n)` should return the nth Fibonacci number, and the module should print `fib(10)` when run as a script. The approach is intentionally small and direct so the plan can be executed and graded mechanically. The contract is centered on the function's numeric outputs and the module's command-line behavior.

## Diagnosis Summary
The repository already contains a Fibonacci implementation in `fib.py`, and the test file `tests/test_fib.py` exercises the expected values for `fib(0)`, `fib(1)`, `fib(2)`, `fib(10)`, and `fib(20)`. The remaining work is to ensure the committed implementation and script entry point continue to satisfy that contract under the pipeline's evidence-driven review process.

## Slices

---

### Slice 1: Verify Fibonacci function and script entry point

**Objective:** Prove that `fib(n)` returns the nth Fibonacci number for the covered inputs and that running `fib.py` prints `55` for `fib(10)`.

#### Acceptance Criteria

- AC-1: `python -m pytest tests/test_fib.py` exits 0 and the committed test log shows `test_fib_0`, `test_fib_1`, `test_fib_2`, `test_fib_10`, and `test_fib_20` passing — verified by `evidence/issue9/slice1/test_run.log`
- AC-2: `python fib.py` prints exactly `55` on stdout for `fib(10)` — verified by `evidence/issue9/slice1/fib_run.log`
- AC-3: `python -m pytest tests/test_fib.py` would fail if `fib(2)` returned `2` or if the `if __name__ == "__main__"` block were missing — verified by `evidence/issue9/slice1/test_run.log` and `evidence/issue9/slice1/fib_run.log`

#### Test Protocol

1. Run `python -m pytest tests/test_fib.py | tee evidence/issue9/slice1/test_run.log` → captures test output → verifies the Fibonacci cases pass.
2. Run `python fib.py | tee evidence/issue9/slice1/fib_run.log` → captures CLI output → verifies the script prints `55`.
3. Re-run `python -m pytest tests/test_fib.py | tee -a evidence/issue9/slice1/test_run.log` after any change to confirm the recorded log still demonstrates the broken-state guards.

## Constraints

- Python: python
- Runner: `python -m pytest`
- Isolation flags: none
- No unauthorized package installations
- No pkill, no rm -rf, no python main.py

## Out of Scope

- Adding new Fibonacci inputs beyond the existing test coverage
- Refactoring the repository into a package layout
- Introducing command-line arguments or input parsing
- Changing the Fibonacci definition away from the standard 0, 1, 1, 2, 3, ... sequence
