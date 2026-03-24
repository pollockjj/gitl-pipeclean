#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = ROOT / "evidence" / "gate_outputs"
PLAN_SKILL = ROOT / ".claude" / "skills" / "qa-plan" / "SKILL.md"
SLICE_SKILL = ROOT / ".claude" / "skills" / "qa-slice" / "SKILL.md"

TDD_BOT_LOGIN = "gitl-tdd[bot]"
TDD_BOT_LOGINS = {"gitl-tdd", "gitl-tdd[bot]"}


def timestamp() -> str:
    return datetime.now().astimezone().strftime("%Y%m%dT%H%M%S")


def log(message: str) -> None:
    stamp = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    print(f"=== [{stamp}] {message} ===", file=sys.stderr)


class FatalError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FatalError(message)


def read_issue_body(repo: str, issue: int, gh_bin: str) -> str:
    command = [gh_bin, "api", f"/repos/{repo}/issues/{issue}", "--jq", ".body"]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise FatalError(f"gh issue fetch failed: {result.stderr.strip() or result.stdout.strip()}")
    body = result.stdout
    require(body.strip() != "", "fetched issue body is empty")
    return body


def read_latest_tdd_comment(repo: str, issue: int, gh_bin: str) -> str:
    """Read the latest comment by gitl-tdd[bot] on the issue — the plan lives here, not in the body."""
    command = [
        gh_bin, "api", f"/repos/{repo}/issues/{issue}/comments",
        "--jq", '[.[] | select(.user.login=="gitl-tdd[bot]")] | last | .body',
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise FatalError(f"gh comment fetch failed: {result.stderr.strip() or result.stdout.strip()}")
    body = result.stdout
    require(body.strip() != "" and body.strip() != "null", "no gitl-tdd[bot] comment found on issue")
    return body


def check_submission_provenance(submission_url: str, repo: str, gh_bin: str) -> None:
    """Verify that the submission comment was posted by the TDD bot."""
    match = re.search(r"issuecomment-(\d+)", submission_url)
    require(match is not None, f"Submission provenance failure: cannot parse comment ID from URL: {submission_url}")
    comment_id = match.group(1)
    result = subprocess.run(
        [gh_bin, "api", f"/repos/{repo}/issues/comments/{comment_id}", "--jq", ".user.login"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise FatalError(f"Submission provenance failure: gh api call failed: {result.stderr.strip()}")
    login = result.stdout.strip()
    if login != TDD_BOT_LOGIN:
        raise FatalError(f"Submission provenance failure: expected {TDD_BOT_LOGIN}, got {login!r}")


def check_plan_provenance(repo: str, issue: int, gh_bin: str) -> None:
    """Verify the last comment on the issue was posted by gitl-tdd[bot]."""
    result = subprocess.run(
        [
            gh_bin,
            "api",
            f"/repos/{repo}/issues/{issue}/comments",
            "--jq",
            ".[-1].user.login // empty",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise FatalError(f"Plan provenance failure: gh api call failed: {result.stderr.strip()}")
    last_author = result.stdout.strip()
    if not last_author:
        raise FatalError("Plan provenance failure: no comments on issue. TDD must post the plan first.")
    if last_author != TDD_BOT_LOGIN:
        raise FatalError(
            f"Plan provenance failure: last comment by {last_author!r}, expected {TDD_BOT_LOGIN}. "
            "TDD must be the last poster before QA runs."
        )


def resolve_command(candidates: list[str]) -> str | None:
    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path
    return None


def resolve_gh() -> str:
    gh_bin = os.environ.get("GH_BIN")
    if gh_bin:
        require(Path(gh_bin).exists(), f"GH_BIN does not exist: {gh_bin}")
        return gh_bin
    resolved = resolve_command(["gh", "gh.exe"])
    require(resolved is not None, "gh binary not found. Set GH_BIN or install GitHub CLI.")
    return resolved


def python_has_post_deps(python_bin: str) -> bool:
    probe = (
        "import importlib.util, sys;"
        "required=('jwt','cryptography','requests');"
        "sys.exit(0 if all(importlib.util.find_spec(name) for name in required) else 1)"
    )
    result = subprocess.run([python_bin, "-c", probe], capture_output=True, text=True, check=False)
    return result.returncode == 0


def resolve_post_python() -> str:
    explicit = os.environ.get("POST_PYTHON")
    if explicit:
        resolved = shutil.which(explicit) or explicit
        require(Path(resolved).exists() or shutil.which(explicit), f"POST_PYTHON is not executable: {explicit}")
        require(python_has_post_deps(resolved), f"POST_PYTHON cannot import jwt, cryptography, and requests: {resolved}")
        return resolved

    candidates = []
    if sys.executable:
        candidates.append(sys.executable)
    candidates.extend(["python", "python3", "py"])

    seen: set[str] = set()
    for candidate in candidates:
        resolved = shutil.which(candidate) or candidate
        if resolved in seen:
            continue
        seen.add(resolved)
        if shutil.which(candidate) or Path(resolved).exists():
            if python_has_post_deps(resolved):
                return resolved
    raise FatalError("no usable Python interpreter found for post_as_app.py with jwt, cryptography, and requests available")


def resolve_codex() -> str:
    explicit = os.environ.get("CODEX_BIN")
    if explicit:
        resolved = shutil.which(explicit) or explicit
        require(Path(resolved).exists() or shutil.which(explicit), f"CODEX_BIN does not exist: {explicit}")
        return resolved
    resolved = resolve_command(["codex", "codex.cmd", "codex.exe", "codex.ps1"])
    require(resolved is not None, "codex binary not found. Set CODEX_BIN or install Codex CLI.")
    return resolved


def invoke_shell_script(command: list[str], stdin_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        input=stdin_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def run_codex(codex_bin: str, prompt_file: Path, repo_root: Path, model: str, reasoning_effort: str | None) -> subprocess.CompletedProcess[str]:
    if codex_bin.lower().endswith(".ps1"):
        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            codex_bin,
            "exec",
        ]
    else:
        command = [codex_bin, "exec"]
    if reasoning_effort:
        command.extend(["-c", f'model_reasoning_effort="{reasoning_effort}"'])
    command.extend(
        [
            "--model",
            model,
            "--dangerously-bypass-approvals-and-sandbox",
            "-C",
            str(repo_root),
            "-",
        ]
    )
    prompt = prompt_file.read_text(encoding="utf-8")
    return invoke_shell_script(command, stdin_text=prompt)


def run_copilot(gh_bin: str, prompt: str, repo_root: Path, model: str) -> subprocess.CompletedProcess[str]:
    command = [
        gh_bin,
        "copilot",
        "--",
        "-p",
        prompt,
        "--model",
        model,
        "--yolo",
        "--allow-all-tools",
        "--no-ask-user",
        "--no-custom-instructions",
        "--add-dir",
        str(repo_root),
    ]
    return invoke_shell_script(command)


def run_claude(prompt: str, repo_root: Path, model: str) -> subprocess.CompletedProcess[str]:
    command = [
        "claude",
        "-p",
        prompt,
        "--model",
        model,
        "--dangerously-skip-permissions",
        "--add-dir",
        str(repo_root),
    ]
    return invoke_shell_script(command)


def extract_verdict_block(mode: str, text: str) -> str:
    heading = "## QA Gate"
    pattern = re.compile(
        rf"^{re.escape(heading)} .*?(?=^tokens used$|^\d{{4}}-\d{{2}}-\d{{2}}T.*\bWARN\b|^{re.escape(heading)} |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    decision_pattern = re.compile(r"^### Decision(?:\(\d+\))?:\s*(PASS|HOLD)\b", re.MULTILINE)
    blocks = [match.group(0).strip() for match in pattern.finditer(text) if decision_pattern.search(match.group(0))]
    if blocks:
        return blocks[-1].rstrip() + "\n"

    # Fallback: some backends emit the contract/evidence/evaluation body without the
    # expected "## QA Gate ..." heading but still include a valid Decision(...) line.
    decision_match = decision_pattern.search(text)
    require(bool(decision_match), "Could not extract a structured verdict block from agent output")

    decision_index = decision_match.start()
    contract_index = text.rfind("CONTRACT —", 0, decision_index)
    start_index = contract_index if contract_index != -1 else 0
    return text[start_index:].strip() + "\n"


def normalize_verdict_block(
    mode: str,
    issue: int,
    slice_number: str | None,
    submission_url: str | None,
    verdict: str,
    comment_text: str,
) -> str:
    if comment_text.startswith("## QA Gate"):
        return comment_text

    evaluated = datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S%z")
    if mode == "slice":
        require(slice_number is not None, "slice mode requires slice number for normalized verdict")
        heading = f"## QA Gate — Slice {slice_number} — {verdict}"
        submission_line = submission_url or "<missing>"
    else:
        heading = f"## QA Gate — Plan — {verdict}"
        submission_line = "n/a"

    # Keep posted comments bounded while preserving the gate's raw evidence.
    raw_excerpt = comment_text.strip()
    if len(raw_excerpt) > 24000:
        raw_excerpt = raw_excerpt[:24000] + "\n...[truncated]..."

    normalized = (
        f"{heading}\n\n"
        f"**Evaluated:** {evaluated}\n"
        f"**Submission comment:** {submission_line}\n\n"
        f"### Decision({issue}): {verdict}\n\n"
        "### Gate Transcript (Raw)\n\n"
        "```text\n"
        f"{raw_excerpt}\n"
        "```\n"
    )
    return normalized


def parse_verdict(comment_text: str, issue: int) -> str:
    m = re.search(rf"^### Decision\({re.escape(str(issue))}\):\s*(PASS|HOLD)", comment_text, re.MULTILINE)
    if m:
        return m.group(1)
    raise FatalError(f"No valid '### Decision({issue}): PASS/HOLD' line found in verdict")


def post_comment(post_python: str, repo: str, issue: int, body_file: Path) -> str:
    command = [post_python, str(ROOT / "scripts" / "post_as_app.py"), "qa", "comment", repo, str(issue), str(body_file)]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise FatalError(f"post_as_app.py failed: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout.strip()


def build_prompt(mode: str, repo: str, issue: int, skill_file: Path, plan_doc_file: Path | None, submission_url: str | None) -> str:
    if mode == "plan":
        require(plan_doc_file is not None, "plan mode requires plan document path")
        return (
            f"Read the skill file {skill_file} and the exact plan file {plan_doc_file}. "
            f"Audit that exact plan file per the skill and output a full verdict that includes a line "
            f"starting with '### Decision({issue}):'. Do not ask follow-up questions. "
            "Do not search for a different plan document. Do not post anything to GitHub."
        )
    submission_clause = f"Submission comment: {submission_url}" if submission_url else ""
    return (
        "You are a stateless QA gate.\n\n"
        f"Read the full skill instructions from: {skill_file}\n\n"
        f"The slice contract document is the GitHub issue body at: https://github.com/{repo}/issues/{issue}\n\n"
        f"Gate slice {{slice_number}} of issue {repo}#{issue}.\n"
        f"The decision line MUST be exactly: '### Decision({issue}): PASS' or '### Decision({issue}): HOLD'.\n"
        f"{submission_clause}\n\n"
        "Fetch the issue body and comments yourself with gh api. Do not ask follow-up questions.\n\n"
        "Use 'gh api' to fetch the issue body and comments. Apply all phases per the skill instructions.\n\n"
        "CRITICAL: Do NOT post your verdict to the issue. Output your complete structured verdict to stdout ONLY. "
        "The gate runner will handle posting. Do NOT run 'gh issue comment' or any posting command."
    )


@dataclass
class GateArgs:
    mode: str
    repo: str
    issue: int
    slice_number: str | None
    submission_comment_url: str | None


class GateRunner:
    def __init__(self, args: GateArgs) -> None:
        self.args = args
        self.repo_root = ROOT
        self.evidence_dir = EVIDENCE_DIR
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.run_timestamp = timestamp()
        self.gh_bin = resolve_gh()
        self.post_python = resolve_post_python()
        self.qa_backend = os.environ.get("QA_BACKEND", "copilot")
        self.qa_copilot_model = os.environ.get("QA_COPILOT_MODEL", "claude-opus-4.6")
        self.qa_claude_model = os.environ.get("QA_CLAUDE_MODEL", "claude-opus-4.6")
        self.qa_codex_model = os.environ.get("QA_CODEX_MODEL", "gpt-5.4")
        self.qa_codex_reasoning_effort = os.environ.get("QA_CODEX_REASONING_EFFORT", "low")
        self.codex_bin = resolve_codex() if self.qa_backend == "codex" else None
        if self.qa_backend not in {"codex", "copilot", "claude"}:
            raise FatalError(f"unsupported QA_BACKEND '{self.qa_backend}' (expected 'codex', 'copilot', or 'claude')")

    def paths(self) -> tuple[Path, Path, Path | None, Path]:
        repo_name = self.args.repo.split("/")[-1]
        if self.args.mode == "plan":
            output = self.evidence_dir / f"qa_plan_{repo_name}_{self.args.issue}_{self.run_timestamp}.md"
            prompt = self.evidence_dir / f"qa_plan_{repo_name}_{self.args.issue}_{self.run_timestamp}.prompt.txt"
            plan_doc = self.evidence_dir / f"qa_plan_{repo_name}_{self.args.issue}_{self.run_timestamp}.issue.md"
            comment = self.evidence_dir / f"qa_plan_{repo_name}_{self.args.issue}_{self.run_timestamp}.comment.md"
            return output, prompt, plan_doc, comment
        slice_number = self.args.slice_number
        require(slice_number is not None, "slice mode requires SLICE_NUMBER argument")
        output = self.evidence_dir / f"qa_slice_{repo_name}_{self.args.issue}_s{slice_number}_{self.run_timestamp}.md"
        prompt = self.evidence_dir / f"qa_slice_{repo_name}_{self.args.issue}_s{slice_number}_{self.run_timestamp}.prompt.txt"
        comment = self.evidence_dir / f"qa_slice_{repo_name}_{self.args.issue}_s{slice_number}_{self.run_timestamp}.comment.md"
        return output, prompt, None, comment

    def run(self) -> int:
        output_file, prompt_file, plan_doc_file, comment_file = self.paths()
        skill_file = PLAN_SKILL if self.args.mode == "plan" else SLICE_SKILL
        require(skill_file.exists(), f"skill file not found: {skill_file}")
        if self.args.mode == "slice" and self.args.submission_comment_url:
            check_submission_provenance(self.args.submission_comment_url, self.args.repo, self.gh_bin)
        check_plan_provenance(self.args.repo, self.args.issue, self.gh_bin)
        if self.args.mode == "plan":
            plan_doc_file.write_text(read_latest_tdd_comment(self.args.repo, self.args.issue, self.gh_bin), encoding="utf-8")
        prompt = build_prompt(
            self.args.mode,
            self.args.repo,
            self.args.issue,
            skill_file,
            plan_doc_file,
            self.args.submission_comment_url,
        )
        if self.args.mode == "slice":
            prompt = prompt.replace("{slice_number}", str(self.args.slice_number))
        prompt_file.write_text(prompt, encoding="utf-8")

        log(f"mode={self.args.mode}")
        log(f"repo={self.args.repo}")
        log(f"issue={self.args.issue}")
        log(f"slice={self.args.slice_number or '<none>'}")
        log(f"output={output_file}")
        log(f"prompt_file={prompt_file}")
        log(f"skill_file={skill_file}")
        log(f"qa_backend={self.qa_backend}")
        log(f"post_python={self.post_python}")

        if self.qa_backend == "copilot":
            result = run_copilot(self.gh_bin, prompt, self.repo_root, self.qa_copilot_model)
        elif self.qa_backend == "claude":
            result = run_claude(prompt, self.repo_root, self.qa_claude_model)
        else:
            assert self.codex_bin is not None
            result = run_codex(
                self.codex_bin,
                prompt_file,
                self.repo_root,
                self.qa_codex_model,
                self.qa_codex_reasoning_effort,
            )

        transcript = (result.stdout or "") + (result.stderr or "")
        output_file.write_text(transcript, encoding="utf-8")
        if result.returncode != 0:
            stderr_tail = (result.stderr or "")[-500:]
            stdout_tail = (result.stdout or "")[-500:]
            raise FatalError(f"QA backend '{self.qa_backend}' exited with code {result.returncode}. Transcript: {output_file}\nstdout tail: {stdout_tail}\nstderr tail: {stderr_tail}")

        comment_text = extract_verdict_block(self.args.mode, transcript)
        verdict = parse_verdict(comment_text, self.args.issue)
        comment_text = normalize_verdict_block(
            self.args.mode,
            self.args.issue,
            self.args.slice_number,
            self.args.submission_comment_url,
            verdict,
            comment_text,
        )
        comment_file.write_text(comment_text, encoding="utf-8")
        log(f"verdict={verdict}")
        comment_url = post_comment(self.post_python, self.args.repo, self.args.issue, comment_file)
        print(f"=== Posted: {comment_url} ===", file=sys.stderr)
        return 0 if verdict == "PASS" else 1


def parse_args() -> GateArgs:
    parser = argparse.ArgumentParser(description="Cross-platform QA gate runner")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    plan_parser = subparsers.add_parser("plan", help="Run qa-plan for an issue")
    plan_parser.add_argument("repo", help="OWNER/REPO")
    plan_parser.add_argument("issue", type=int, help="Issue number")

    slice_parser = subparsers.add_parser("slice", help="Run qa-slice for an issue slice")
    slice_parser.add_argument("repo", help="OWNER/REPO")
    slice_parser.add_argument("issue", type=int, help="Issue number")
    slice_parser.add_argument("slice_number", help="Slice number")
    slice_parser.add_argument("submission_comment_url", nargs="?", help="Submission comment URL")

    namespace = parser.parse_args()
    return GateArgs(
        mode=namespace.mode,
        repo=namespace.repo,
        issue=namespace.issue,
        slice_number=getattr(namespace, "slice_number", None),
        submission_comment_url=getattr(namespace, "submission_comment_url", None),
    )


def main() -> int:
    try:
        args = parse_args()
        return GateRunner(args).run()
    except FatalError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
