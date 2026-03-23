# gitl-pipeclean

## Repository Role

This is a workspace repository. Work is tracked via GitHub Issues. Agents implement slices of work defined in issues and push code to trigger automated evaluation.

## Branch Naming

Branches must follow this pattern:

```
issue{N}/slice{M}
```

Example: `issue12/slice2`

CI workflows trigger only on branches matching `issue*/slice*`.

## Workflow Mechanics

1. Issues are created by `gitl-tdd[bot]`.
2. An agent creates the branch, implements the required changes, and tests locally during development.
3. When the agent is satisfied the code is correct, it pushes the branch.
4. CI runs the official tests and commits evidence artifacts via `github-actions[bot]`. This CI-produced evidence is what the QA gate evaluates.
5. QA verdicts are posted to the issue by `gitl-qa[bot]`.

**Local test runs are development feedback. CI test runs are official evidence.** The agent may run tests freely during development. Only CI-committed artifacts are evaluated by the QA gate.

## Bot Identities

| Bot | Role |
|:----|:-----|
| `gitl-tdd[bot]` | Creates issues with slice acceptance criteria |
| `github-actions[bot]` | Runs CI, commits evidence artifacts to the branch |
| `gitl-qa[bot]` | Posts QA verdicts on issues |
