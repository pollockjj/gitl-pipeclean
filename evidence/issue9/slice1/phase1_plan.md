## Slice 1 TDD Plan: Verify Fibonacci function and script entry point

### Objective
Prove that `fib(n)` returns the nth Fibonacci number for the covered inputs and that running `fib.py` prints `55` for `fib(10)`.

### Acceptance Criteria

- AC-1: `python -m pytest tests/test_fib.py` exits 0 and the committed test log shows `test_fib_0`, `test_fib_1`, `test_fib_2`, `test_fib_10`, and `test_fib_20` passing — verified by `evidence/issue9/slice1/test_run.log`
- AC-2: `python fib.py` prints exactly `55` on stdout for `fib(10)` — verified by `evidence/issue9/slice1/fib_run.log`
- AC-3: `python -m pytest tests/test_fib.py` would fail if `fib(2)` returned `2` or if the `if __name__ == "__main__"` block were missing — verified by `evidence/issue9/slice1/test_run.log` and `evidence/issue9/slice1/fib_run.log`

### Test Protocol

1. Run `python3 -m pytest tests/test_fib.py | tee evidence/issue9/slice1/test_run.log` → captures test output → verifies the Fibonacci cases pass.
2. Run `python3 fib.py | tee evidence/issue9/slice1/fib_run.log` → captures CLI output → verifies the script prints `55`.
3. Re-run `python3 -m pytest tests/test_fib.py | tee -a evidence/issue9/slice1/test_run.log` after any change to confirm the recorded log still demonstrates the broken-state guards.
