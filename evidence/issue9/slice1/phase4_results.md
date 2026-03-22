## Slice 1 TDD Results — COMPLETE

**Submitted:** 2026-03-22T19:40:00Z
**Commit SHA:** 938c905e3f47a3cde9eb35f6c4139484210292d0
**Evidence directory:** evidence/issue9/slice1/ @ 938c905e3f47a3cde9eb35f6c4139484210292d0

### Evidence Manifest

- [E-1] phase1-plan — evidence/issue9/slice1/phase1_plan.md — slice contract posted to the issue
- [E-2] test-run-log — evidence/issue9/slice1/test_run.log — pytest output showing 5 passing tests
- [E-3] fib-run-log — evidence/issue9/slice1/fib_run.log — script output showing 55
- [E-4] sha256sums — evidence/issue9/slice1/sha256sums.txt — checksums for committed evidence

### Acceptance Criteria Status

| # | Criterion | Status | Evidence |
|:--|:--|:--|:--|
| AC-1 | `python -m pytest tests/test_fib.py` exits 0 and the committed test log shows `test_fib_0`, `test_fib_1`, `test_fib_2`, `test_fib_10`, and `test_fib_20` passing — verified by `evidence/issue9/slice1/test_run.log` | DONE | [E-2] |
| AC-2 | `python fib.py` prints exactly `55` on stdout for `fib(10)` — verified by `evidence/issue9/slice1/fib_run.log` | DONE | [E-3] |
| AC-3 | `python -m pytest tests/test_fib.py` would fail if `fib(2)` returned `2` or if the `if __name__ == "__main__"` block were missing — verified by `evidence/issue9/slice1/test_run.log` and `evidence/issue9/slice1/fib_run.log` | DONE | [E-2], [E-3] |

### Summary

`fib.py` returns the expected Fibonacci values for the tested inputs, and the module entry point prints `55` for `fib(10)`. The evidence logs and checksums are recorded in the slice evidence directory.
