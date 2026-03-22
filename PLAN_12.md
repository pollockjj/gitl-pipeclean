# Plan: Prove is_prime(n) Correctness

## Overview

Write a Python function `is_prime(n)` that returns `True` if `n` is prime, `False` otherwise, with a `__main__` block that prints `is_prime(17)`. Verify correctness via pytest with CI-collected evidence covering prime identification, non-prime rejection, edge cases, and main-block output.

## Diagnosis Summary

This is a greenfield implementation — no existing code or bug to diagnose. The function `is_prime` does not yet exist in the repository. The verification strategy is to write comprehensive tests that exercise both the function logic and the main-block output, then let CI collect evidence that all tests pass.

## Current State

- `fib.py` — complete, contains `fib(n)` function with `__main__` block (pattern to follow)
- `tests/test_fib.py` — complete, tests for `fib()` (pattern to follow)
- `is_prime.py` — does not exist (to be created)
- `tests/test_is_prime.py` — does not exist (to be created)
- `.github/workflows/slice-evidence.yml` — complete, runs `pytest tests/ -v`, commits evidence

## Slices

---

### Slice 1: Prove is_prime(n) correctly identifies primes and non-primes with correct main-block output

**Objective:** Prove that `is_prime(n)` returns `True` for known primes, `False` for known non-primes and edge cases, and that the `__main__` block prints `True` (the result of `is_prime(17)`).

#### Acceptance Criteria

- AC-1: `tests/test_is_prime.py::test_is_prime_17 PASSED` appears in `evidence/issue12/slice1/test_run.log`, confirming `is_prime(17)` returns `True` — verified by CI-committed `evidence/issue12/slice1/test_run.log`
- AC-2: `pytest tests/ -v` exits 0 with tests for primes (2, 3, 5, 17) returning `True` and non-primes (0, 1, 4, 9) returning `False`, all marked PASSED in `evidence/issue12/slice1/test_run.log` and the log contains `EXIT_CODE: 0` — verified by CI-committed `evidence/issue12/slice1/test_run.log`
- AC-3: `tests/test_is_prime.py::test_main_output PASSED` appears in `evidence/issue12/slice1/test_run.log`, confirming the `if __name__ == "__main__"` block in `is_prime.py` prints `True` to stdout — verified by CI-committed `evidence/issue12/slice1/test_run.log`
- AC-4: `evidence/issue12/slice1/sha256sums.txt` exists and is committed by `github-actions[bot]` — verified by fetching `evidence/issue12/slice1/sha256sums.txt` at the CI evidence commit ref

---

## Constraints

- Python: python3
- Runner: pytest (via CI workflow)
- Evidence collected by GitHub Actions only — agent does not run tests for evidence
- No unauthorized package installations
- No pkill, no rm -rf

## Out of Scope

- Modifying the existing `fib.py` or `tests/test_fib.py`
- Performance optimization of `is_prime` for large numbers
- Adding type stubs or mypy configuration
- Modifying the CI workflow
