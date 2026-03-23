# gitl-pipeclean

Workspace repository for coding agent runs. Agents open issues here, push code to branches, and CI collects evidence artifacts.

## Workflow

- Agents create GitHub issues to track work items
- Code is pushed to branches matching the pattern `issue*/slice*`
- CI runs tests on push via `.github/workflows/slice-evidence.yml` and commits evidence artifacts back to the branch

## Bots

| Actor | Role |
|:------|:-----|
| `gitl-tdd[bot]` | Posts implementation notes and status updates to issues |
| `gitl-qa[bot]` | Posts evaluation results to issues |
| `github-actions[bot]` | Commits CI evidence artifacts to branches |

## Branch Naming

Branches must match `issue*/slice*` to trigger the CI workflow.

Example: `issue42/slice1`

## Artifacts

CI artifacts are committed directly to the branch under `evidence/` by `github-actions[bot]` after each run.
