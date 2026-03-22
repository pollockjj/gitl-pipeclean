## Slice 2 TDD Plan: CI evidence workflow — tests run by GitHub Actions, not by the agent

### Objective
Prove that pushing code to a branch triggers a CI workflow that independently runs the test protocol, commits log artifacts to the evidence directory, and posts a Phase 4 results comment as `gitl-tdd[bot]` — with no agent shell commands involved in test execution or posting.

### Acceptance Criteria

- AC-1: `.github/workflows/slice-evidence.yml` exists and defines a workflow triggered on push to branches matching `issue*/slice*` — verified by `evidence/issue11/slice2/workflow_file.log` at the evidence commit SHA containing the `cat` output of the workflow file
- AC-2: A test push to a branch `issue11/slice2-test` triggers the workflow, which runs `python -m pytest tests/test_fib.py -v` and commits `evidence/issue11/slice2/test_run.log` — verified by the GitHub Actions run URL in `evidence/issue11/slice2/ci_run.log` showing a completed run with exit code 0
- AC-3: The workflow posts a Phase 4 results comment to issue #11 as `gitl-tdd[bot]` — verified by `evidence/issue11/slice2/ci_comment.log` at the evidence commit SHA containing the comment URL and author login `gitl-tdd[bot]`
- AC-4: The agent-authored code commit and the CI-authored evidence commit have different commit authors — verified by `evidence/issue11/slice2/commit_authors.log` at the evidence commit SHA showing two distinct author identities

### Test Protocol

1. Create `.github/workflows/slice-evidence.yml` with workflow triggered on `push` to `issue*/slice*` branches
2. Configure GitHub Actions secrets: `GITL_TDD_APP_ID`, `GITL_TDD_INSTALL_ID`, `GITL_TDD_PEM` for posting
3. Create branch `issue11/slice2-test`, push test code
4. Wait for workflow to complete — `gh run list --branch issue11/slice2-test`
5. Verify workflow ran pytest, committed evidence, and posted comment
6. `cat .github/workflows/slice-evidence.yml > evidence/issue11/slice2/workflow_file.log`
7. Record the Actions run URL in `evidence/issue11/slice2/ci_run.log`
8. Record the comment URL and author in `evidence/issue11/slice2/ci_comment.log`
9. `git log --format="%H %an" HEAD~2..HEAD > evidence/issue11/slice2/commit_authors.log` to show distinct authors
