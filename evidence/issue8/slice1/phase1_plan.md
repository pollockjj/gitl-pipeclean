## Slice 1 TDD Plan: Prove fib(n) correctness and main block output

### Objective

Prove that `fib(n)` returns the correct Fibonacci number for boundary and interior values, and that the main block prints exactly `55` to stdout.

### Acceptance Criteria

- AC-1: `python3 fib.py` exits 0 and stdout contains exactly one line reading `55` — verified by `evidence/issue8/slice1/fib_run.log` containing the captured stdout and exit code
- AC-2: `python3 -m pytest tests/test_fib.py -v` exits 0 with 5 or more tests passing, covering at minimum fib(0)=0, fib(1)=1, fib(2)=1, fib(10)=55, and fib(20)=6765 — verified by `evidence/issue8/slice1/test_run.log` containing the pytest output showing each named test and exit code 0
- AC-3: `python3 -c "from fib import fib; print(type(fib(10)))"` prints `<class 'int'>` and exits 0 — verified by `evidence/issue8/slice1/type_check.log` containing stdout and exit code

### Test Protocol

1. `python3 fib.py 2>&1 | tee evidence/issue8/slice1/fib_run.log; echo "EXIT_CODE: $?" >> evidence/issue8/slice1/fib_run.log` → captures stdout and exit code → verifies AC-1
2. `python3 -m pytest tests/test_fib.py -v 2>&1 | tee evidence/issue8/slice1/test_run.log; echo "EXIT_CODE: $?" >> evidence/issue8/slice1/test_run.log` → captures pytest output → verifies AC-2
3. `python3 -c "from fib import fib; print(type(fib(10)))" 2>&1 | tee evidence/issue8/slice1/type_check.log; echo "EXIT_CODE: $?" >> evidence/issue8/slice1/type_check.log` → captures type output → verifies AC-3
