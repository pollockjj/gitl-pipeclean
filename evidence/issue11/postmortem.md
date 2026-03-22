## Post-Mortem — Issue #11: Pipeline Hardening

### Execution Summary
- 3 slices, all PASS
- Slice 1: skill edits (path standardization, pytest -v, Current State template) — PASS first try
- Slice 2: CI evidence workflow — PASS first try
- Slice 3: validation hello world (#12) with hardened pipeline — PASS first try, zero HOLDs

### Plan Phase
- 2 plan HOLDs before PASS (attempts 1-3)
- HOLD 1: Check 8 (diagnosis completeness) — I wrote a PLAN-mode summary that contained enough diagnosis detail to trigger INVESTIGATE mode. The QA gate correctly demanded full INVESTIGATE elements.
- HOLD 2: Check 7 + 12 (diagnostic fit + scope containment) — I smuggled two nice-to-have ACs (.gitignore, single-commit recommendation) into an INVESTIGATE-mode plan where they weren't tied to diagnosed failures. The QA gate correctly rejected them as scope bleed.

### What the Pipeline Caught
The QA gate prevented me from shipping a plan with scope bleed twice. Both times I was trying to bundle unrelated improvements into the plan. Both times the gate was right — those ACs would have passed regardless of whether the diagnosed failures were fixed.

### CI Integration Outcome
The CI workflow (`slice-evidence.yml`) eliminates three classes of failure:
1. Shell heredoc corruption (agent never generates posting commands)
2. Evidence fabrication (agent never commits test output)
3. Pytest verbosity mistakes (CI workflow hardcodes `-v`)

The identity separation is now three-way: agent pushes code, CI runs tests and commits evidence, QA evaluates evidence. No entity controls more than one leg.

### Suggestion for Improvement
The plan phase took 3 attempts because the skill's mode detection (PLAN vs INVESTIGATE) is triggered by content in the Diagnosis Summary section. A plan that includes root cause analysis triggers INVESTIGATE mode and its stricter Check 8, even if the planner intended PLAN mode. The tdd-plan skill should explicitly allow the planner to declare the mode, or the mode detection heuristic should be documented more clearly so planners can write Diagnosis Summaries that don't accidentally trigger the wrong mode.
