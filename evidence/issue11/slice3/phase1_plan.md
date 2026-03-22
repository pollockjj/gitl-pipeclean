## Slice 3 TDD Plan: Validate hardened pipeline with zero avoidable HOLDs

### Objective
Prove that a full E2E pipeline run (tdd-plan → qa-plan → tdd-slice → qa-slice) on a new hello world issue using hardened skills and CI evidence posting produces zero HOLDs caused by evidence path mismatches, pytest verbosity, or markdown corruption.

### Acceptance Criteria

- AC-1: A new issue is created and the full pipeline completes (qa-plan PASS + qa-slice PASS) — verified by `evidence/issue11/slice3/pipeline_run.log` at the evidence commit SHA containing both PASS verdict URLs
- AC-2: Every HOLD (if any) in the pipeline run is categorized, and none are caused by evidence path mismatch, pytest verbosity, or shell heredoc corruption — verified by `evidence/issue11/slice3/hold_analysis.log` at the evidence commit SHA. If zero HOLDs, the log contains "0 HOLDs — no analysis required"
- AC-3: All evidence artifacts in the pipeline run are committed by the CI workflow, not by the implementing agent — verified by `evidence/issue11/slice3/evidence_authors.log` at the evidence commit SHA showing CI as the committer for all evidence files

### Test Protocol

1. Create a new issue on pollockjj/gitl-pipeclean with a simple coding task (fib variant or similar)
2. Launch Copilot CLI with hardened skills, full autonomous pipeline
3. Observe: does the agent push to an `issue{N}/slice{M}` branch to trigger CI?
4. Record all PASS/HOLD verdicts in `pipeline_run.log`
5. If any HOLDs occur, categorize each in `hold_analysis.log` — flag if caused by the three diagnosed issues
6. Check git log for evidence commit authors in `evidence_authors.log`
