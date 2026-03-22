## Slice 1 TDD Plan: Standardize evidence paths, pytest verbosity, and plan template across all skills

### Objective
Prove that all four SKILL.md files use the canonical `evidence/issue{ISSUE_NUMBER}/slice{N}/` path pattern, that tdd-slice mandates `pytest -v`, and that the tdd-plan template includes a "Current State" section.

### Acceptance Criteria

- AC-1: `grep -rn 'evidence/slice[0-9N]' .claude/skills/*/SKILL.md` returns zero matches (no bare `evidence/sliceN/` without `issue{ISSUE_NUMBER}/` prefix) — verified by `evidence/issue11/slice1/grep_paths.log` at the evidence commit SHA showing zero lines of output
- AC-2: `grep -n 'pytest.*-v' .claude/skills/tdd-slice/SKILL.md` returns at least one match in the evidence collection rules section mandating `-v` on all pytest invocations — verified by `evidence/issue11/slice1/grep_pytest.log` at the evidence commit SHA
- AC-3: `grep -n 'Current State' .claude/skills/tdd-plan/SKILL.md` returns at least one match in the Phase 5 issue body template section — verified by `evidence/issue11/slice1/grep_template.log` at the evidence commit SHA

### Test Protocol

1. `grep -rn 'evidence/slice[0-9N]' .claude/skills/*/SKILL.md > evidence/issue11/slice1/grep_paths.log 2>&1; echo "EXIT: $?" >> evidence/issue11/slice1/grep_paths.log` → captures grep_paths.log → verifies zero content lines (only EXIT line)
2. `grep -n 'pytest.*-v' .claude/skills/tdd-slice/SKILL.md > evidence/issue11/slice1/grep_pytest.log 2>&1` → captures grep_pytest.log → verifies at least one match
3. `grep -n 'Current State' .claude/skills/tdd-plan/SKILL.md > evidence/issue11/slice1/grep_template.log 2>&1` → captures grep_template.log → verifies at least one match
