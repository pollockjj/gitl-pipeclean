## Slice 1 TDD Plan: Prove Fibonacci outputs and script entry point

### Objective
Prove that `fib(n)` returns the expected Fibonacci numbers for the repository's covered inputs and that running `fib.py` prints `55` for `fib(10)`.

### Acceptance Criteria

- AC-1: `python3 -m pytest tests/test_fib.py -vv` exits 0 and the log fetched from `evidence/slice1/test_run.log` at the Phase 4 submission commit SHA contains `tests/test_fib.py::test_fib_0 PASSED`, `tests/test_fib.py::test_fib_1 PASSED`, `tests/test_fib.py::test_fib_2 PASSED`, `tests/test_fib.py::test_fib_10 PASSED`, and `tests/test_fib.py::test_fib_20 PASSED` — verified by `evidence/slice1/test_run.log` at the submission commit SHA
- AC-2: `python3 fib.py` exits 0 and the log fetched from `evidence/slice1/fib_run.log` at the Phase 4 submission commit SHA contains exactly `55` as its only stdout line — verified by `evidence/slice1/fib_run.log` at the submission commit SHA

### Test Protocol

1. `python3 -m pytest tests/test_fib.py -vv | tee evidence/issue10/slice1/test_run.log > evidence/slice1/test_run.log` → captures the verbose pytest log in both slice namespaces → verifies the covered Fibonacci outputs.
2. `python3 fib.py | tee evidence/issue10/slice1/fib_run.log > evidence/slice1/fib_run.log` → captures script stdout in both slice namespaces → verifies the CLI output is exactly `55`.
3. `sha256sum evidence/issue10/slice1/phase1_plan.md evidence/issue10/slice1/test_run.log evidence/issue10/slice1/fib_run.log evidence/slice1/test_run.log evidence/slice1/fib_run.log > evidence/issue10/slice1/sha256sums.txt` → captures revision-bound checksums → verifies every collected artifact has a sha256 record.
