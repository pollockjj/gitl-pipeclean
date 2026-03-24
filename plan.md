## Overview
Implement the required C/C++ program that reads exactly two integers from stdin and prints their sum. The executable will be built via the provided CMake workflow, run as `./code`, and verified through automated evidence logs that cover the sample case and an important boundary case while ensuring the repository ignores CMake artifacts.

## Diagnosis Summary
No implementation currently exists; the goal is to supply a minimal main that parses two whitespace-separated integers, computes their sum with standard C++ integer arithmetic, and prints the result as a single line, per the issue specification.

## Slices
---
### Slice 1: Sum binary with sample and boundary checks
**Objective:** Confirm that building the project produces the `code` binary and that it produces the expected outputs for the provided sample and a representative boundary pair.
#### Acceptance Criteria
- AC-1: `cmake . && make` completes with exit code 0 and leaves the `code` binary in the project root, captured in `evidence/slice1/build.log`; this proves the build pipeline can produce the expected executable before runtime verification.
- AC-2: Running `./code` with stdin `1 1` prints exactly `2` followed by a newline, captured in `evidence/slice1/sample1.log`, proving the program implements the example specification.
- AC-3: Running `./code` with stdin `-1000000000 1000000000` prints `0` followed by a newline, captured in `evidence/slice1/boundary.log`, proving the implementation handles a negative-plus-positive sum within a typical 32-bit signed range.
- AC-4: `.gitignore` contains at least the lines `CMakeFiles/` and `CMakeCache.txt`, verified by `evidence/slice1/gitignore.txt`, proving generated CMake artifacts are excluded.

## Constraints
- Python: python
- Runner: cmake && make
- Isolation flags: none beyond the provided sandbox
- No unauthorized package installations
- No pkill, no rm -rf, no python main.py
- No disk usage is permitted outside of building and producing the required artifacts

## Out of Scope
- Handling more than two integers or additional input formatting beyond the single-line, space-separated pair
- Implementing defensive parsing for malformed input (the judge guarantees two integers)
- Supporting big integers or arbitrary-precision arithmetic beyond what 32-bit `int` already provides
