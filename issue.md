## Problem Description

Implement an ICPC (International Collegiate Programming Contest) management system that handles team registration, submissions, scoreboard management with freeze/scroll mechanics, and various queries.

## Background

In ICPC competitions, each team attempts to solve the maximum number of problems with the minimum number of incorrect submissions. The winner is the team that correctly solves the most problems with the least total penalty time.

## Terminology

- **Competition Time**: An integer in `[1, duration_time]`. Submission times are monotonically non-decreasing.
- **Team**: Unique name of uppercase/lowercase letters, digits, and underscores (max 20 chars).
- **Judge Status**: `Accepted`, `Wrong_Answer`, `Runtime_Error`, `Time_Limit_Exceed`. Only `Accepted` counts as passing.
- **Penalty Time**: For a solved problem: `P = 20X + T` where `X` = incorrect attempts before first AC, `T` = time of first AC. Total penalty = sum over all solved problems.
- **Ranking** (multi-key sort):
  1. More solved problems → higher rank
  2. Tie: less penalty time → higher rank
  3. Tie: compare maximum solve times (descending), then second-max, etc.
  4. Tie: lexicographically smaller team name → higher rank
  5. Frozen problems are excluded from ranking. Before first flush, rank by team name.
- **Freeze**: After freezing, unsolved problems' new submissions are hidden on the scoreboard. Only submission count during freeze is shown. Problems with post-freeze submissions enter frozen state.
- **Scroll**: Iteratively unfreeze the lowest-ranked team's smallest-numbered frozen problem, recalculate rankings, until no frozen problems remain. Scroll first flushes the scoreboard. Multiple freeze/scroll cycles can occur.

## Commands

```
ADDTEAM [team_name]
START DURATION [duration_time] PROBLEM [problem_count]
SUBMIT [problem_name] BY [team_name] WITH [submit_status] AT [time]
FLUSH
FREEZE
SCROLL
QUERY_RANKING [team_name]
QUERY_SUBMISSION [team_name] WHERE PROBLEM=[problem_name] AND STATUS=[status]
END
```

### ADDTEAM
- Success: `[Info]Add successfully.\n`
- Competition started: `[Error]Add failed: competition has started.\n`
- Duplicate name: `[Error]Add failed: duplicated team name.\n`

### START
- Success: `[Info]Competition starts.\n`
- Already started: `[Error]Start failed: competition has started.\n`

### SUBMIT
- No output. Records submission. Input guaranteed valid.

### FLUSH
- Output: `[Info]Flush scoreboard.\n`

### FREEZE
- Success: `[Info]Freeze scoreboard.\n`
- Already frozen: `[Error]Freeze failed: scoreboard has been frozen.\n`

### SCROLL
- Not frozen: `[Error]Scroll failed: scoreboard has not been frozen.\n`
- Frozen:
  1. Output `[Info]Scroll scoreboard.\n`
  2. Output scoreboard before scrolling (after flush)
  3. Output each ranking-changing unfreeze: `[team_name1] [team_name2] [solved_number] [penalty_time]`
  4. Output scoreboard after scrolling

Scoreboard format (N lines, one per team):
```
team_name ranking solved_count total_penalty A B C ...
```

Problem display:
- Solved (not frozen): `+x` (or `+` if x=0)
- Not solved (not frozen): `-x` (or `.` if x=0)
- Frozen: `-x/y` (or `0/y` if x=0) where x=pre-freeze wrong attempts, y=post-freeze submissions

### QUERY_RANKING
- Team not found: `[Error]Query ranking failed: cannot find the team.\n`
- Found: `[Info]Complete query ranking.\n` then if frozen: `[Warning]Scoreboard is frozen. The ranking may be inaccurate until it were scrolled.\n` then: `[team_name] NOW AT RANKING [ranking]`

### QUERY_SUBMISSION
- Team not found: `[Error]Query submission failed: cannot find the team.\n`
- Found: `[Info]Complete query submission.\n` then either `Cannot find any submission.\n` or `[team_name] [problem_name] [status] [time]`

### END
- Output: `[Info]Competition ends.\n`

## Data Constraints

For 60% of data: N ≤ 500, operations ≤ 10^4.
For 100% of data: N ≤ 10^4 teams, M ≤ 26 problems, T ≤ 10^5, operations ≤ 3×10^5, flush ≤ 1000, freeze ≤ 10.

## Per-Testcase Resource Limits

- **Time Limit (per test case)**: 2000 ms
- **Memory Limit (per test case)**: 512 MiB
- **Disk Usage**: No disk usage is permitted.

## Build System

Your solution will be compiled using the following process:

1. If `CMakeLists.txt` exists: `cmake .`
2. If `GNUmakefile`/`makefile`/`Makefile` exists: `make`
3. The compiled binary must be named `code` in the project root directory.

You must create your own `CMakeLists.txt`. The environment has gcc-13 and g++-13.

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

Your solution will be evaluated by an automated CI judge against hidden test cases. The judge runs your compiled `code` binary against each test case and compares output exactly. Partial credit is awarded per test case passed. The CI judge also submits your code to an external grading system (ACMOJ) which returns an official score.

**CI results are ground truth.** The CI judge posts evidence including:
- Local test case results (PASS/FAIL per case, with SCORE: X/Y)
- ACMOJ submission score (official external judge)

**A failing CI run means the code is wrong.** Your acceptance criteria MUST include:
- AC requiring CI workflow conclusion `success` on the branch
- AC requiring SCORE in build.log showing all local test cases passing
- AC requiring ACMOJ score > 0 in acmoj_result.log

Any plan that does not include these CI-based ACs will be rejected by the QA gate. The QA gate will NOT pass a slice where the CI evidence shows test failures or ACMOJ score of 0.

Your plan must account for:
- All boundary conditions described or implied by the spec
- The freeze/scroll mechanics which are the primary source of bugs
- Performance within the time limits for 100% data constraints
- A production-ready, submission-quality result

## Mandatory Workflow

This issue MUST be executed using the TDD pipeline skills. You MUST:

1. Execute tdd-plan against this issue — produce a plan with acceptance criteria, post it to this issue, and pass the qa-plan gate before writing any code.
2. Execute tdd-slice for each slice — implement, collect evidence, post results, and pass the qa-slice gate.
3. No phase may be skipped. No code may be written before the plan passes qa-plan. No slice may proceed without qa-slice PASS.

Direct implementation without planning is a protocol violation.
