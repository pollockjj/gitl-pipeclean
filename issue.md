## Problem Description

Input two integers and output their sum.

## Input Format

A single line containing two integers, A and B, separated by a space.

## Output Format

A single number, the sum of A + B.

## Sample

### Input

```
1 1
```

### Output

```
2
```

## Per-Testcase Resource Limits

- **Time Limit (per test case)**: 1000 ms
- **Memory Limit (per test case)**: 256 MiB
- **Disk Usage**: No disk usage is permitted.

## Build System

Your solution will be compiled using the following process:

1. If `CMakeLists.txt` exists: `cmake .`
2. If `GNUmakefile`/`makefile`/`Makefile` exists: `make`
3. The compiled binary must be named `code` in the project root directory.

A starter `CMakeLists.txt` is provided in your workspace at `./CMakeLists.txt`. You may use or modify it. The environment has gcc-13 and g++-13.

## Repository Requirements

- You must create a `.gitignore` file excluding at minimum:
  ```
  CMakeFiles/
  CMakeCache.txt
  ```
- Language: C or C++
- The program reads from standard input and writes to standard output
- Output must exactly match expected output including format

## Grading

Your solution will be evaluated by an automated judge against hidden test cases including edge cases. Your plan must account for:
- All boundary conditions described or implied by the spec
- A production-ready, submission-quality result

The QA gate evaluates your work against acceptance criteria you define. Those criteria must be rigorous enough that passing them means passing the external judge.

## Mandatory Workflow

This issue MUST be executed using the TDD pipeline skills. You MUST:

1. Execute tdd-plan against this issue — produce a plan with acceptance criteria, post it to this issue, and pass the qa-plan gate before writing any code.
2. Execute tdd-slice for each slice — implement, collect evidence, post results, and pass the qa-slice gate.
3. No phase may be skipped. No code may be written before the plan passes qa-plan. No slice may proceed without qa-slice PASS.

Direct implementation without planning is a protocol violation.
