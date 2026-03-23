#!/usr/bin/env python3
"""Post to GitHub as a bot app identity.

Usage:
    post_as_app.py {tdd|qa} comment OWNER/REPO ISSUE_NUMBER BODY_FILE
    post_as_app.py {tdd|qa} comment OWNER/REPO ISSUE_NUMBER --body "inline text"
    cat body.md | post_as_app.py {tdd|qa} comment OWNER/REPO ISSUE_NUMBER
    post_as_app.py tdd create-issue OWNER/REPO --title "Title" BODY_FILE
    post_as_app.py tdd create-issue OWNER/REPO --title "Title" --label tdd-plan BODY_FILE
    post_as_app.py tdd update-issue OWNER/REPO ISSUE_NUMBER BODY_FILE

Reads the PEM key from the platform default key directory by default, generates a JWT, gets an installation
token, posts, verifies, and prints the URL. Exits non-zero on any failure.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path, PureWindowsPath

try:
    import jwt
    import requests
except ImportError:
    print("FATAL: pip install PyJWT cryptography requests", file=sys.stderr)
    sys.exit(2)

AGENTS = {
    "tdd": {
        "app_id": "3158490",
        "install_id": "118256592",
        "key": "gitl-tdd.pem",
        "login": "gitl-tdd[bot]",
    },
    "qa": {
        "app_id": "3158523",
        "install_id": "118258230",
        "key": "gitl-qa.pem",
        "login": "gitl-qa[bot]",
    },
}

# Incoming provenance: who must have posted last before this agent can post
EXPECTED_LAST_POSTER = {
    "tdd": {"gitl-qa[bot]", None},  # None = zero comments (first post)
    "qa": {"gitl-tdd[bot]"},
}


def default_keys_dir() -> Path:
    if sys.platform.startswith("win"):
        program_data = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData"))
        windows_path = PureWindowsPath(str(program_data)) / "gitl" / "github-apps"
        return Path(str(windows_path))
    return Path("/etc/gitl/github-apps")


def get_token(agent_id: str, keys_dir: Path) -> str:
    cfg = AGENTS[agent_id]
    pem_path = keys_dir / cfg["key"]
    if not pem_path.exists():
        print(f"FATAL: PEM not found: {pem_path}", file=sys.stderr)
        sys.exit(1)
    pem = pem_path.read_text()
    now = int(time.time())
    encoded = jwt.encode(
        {"iat": now - 60, "exp": now + 540, "iss": cfg["app_id"]},
        pem,
        algorithm="RS256",
    )
    h = {
        "Authorization": f"Bearer {encoded}",
        "Accept": "application/vnd.github+json",
    }
    r = requests.post(
        f"https://api.github.com/app/installations/{cfg['install_id']}/access_tokens",
        headers=h,
    )
    r.raise_for_status()
    return r.json()["token"]


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }


def get_last_comment_author(token: str, repo: str, issue: int) -> str | None:
    """Return the login of the last commenter, or None if no comments."""
    r = requests.get(
        f"https://api.github.com/repos/{repo}/issues/{issue}/comments?per_page=100",
        headers=_headers(token),
    )
    r.raise_for_status()
    comments = r.json()
    if not comments:
        return None
    return comments[-1]["user"]["login"]


def check_incoming_provenance(agent_id: str, token: str, repo: str, issue: int) -> None:
    """Verify the last comment was posted by the expected identity."""
    last_author = get_last_comment_author(token, repo, issue)
    expected = EXPECTED_LAST_POSTER[agent_id]
    if last_author not in expected:
        expected_str = " or ".join(repr(e) for e in expected if e is not None) or "no comments"
        actual_str = repr(last_author) if last_author else "no comments"
        print(
            f"FATAL: {agent_id.upper()} incoming provenance failure. "
            f"Last comment by {actual_str}, expected {expected_str}.",
            file=sys.stderr,
        )
        sys.exit(1)


def check_outgoing_provenance(agent_id: str, token: str, repo: str, comment_id: int) -> None:
    """Verify the comment we just posted is authored by the correct bot identity."""
    expected_login = AGENTS[agent_id]["login"]
    v = requests.get(
        f"https://api.github.com/repos/{repo}/issues/comments/{comment_id}",
        headers=_headers(token),
    )
    v.raise_for_status()
    actual_login = v.json()["user"]["login"]
    if actual_login != expected_login:
        print(
            f"FATAL: {agent_id.upper()} outgoing provenance failure. "
            f"Comment posted as {actual_login!r}, expected {expected_login!r}.",
            file=sys.stderr,
        )
        sys.exit(1)


def post_comment(token: str, repo: str, issue: int, body: str, agent_id: str | None = None) -> str:
    # Incoming provenance check
    if agent_id is not None:
        check_incoming_provenance(agent_id, token, repo, issue)

    r = requests.post(
        f"https://api.github.com/repos/{repo}/issues/{issue}/comments",
        headers=_headers(token),
        json={"body": body},
    )
    r.raise_for_status()
    comment_id = r.json()["id"]
    html_url = r.json()["html_url"]

    # Outgoing provenance check
    if agent_id is not None:
        check_outgoing_provenance(agent_id, token, repo, comment_id)

    # Verify post content
    v = requests.get(
        f"https://api.github.com/repos/{repo}/issues/comments/{comment_id}",
        headers=_headers(token),
    )
    if v.status_code != 200:
        print(f"FATAL: Post verification failed. Comment {comment_id} not found (HTTP {v.status_code})", file=sys.stderr)
        sys.exit(1)
    if body.startswith("## QA Gate"):
        posted_body = v.json().get("body", "")
        if not re.search(r"^### Decision(?:\(\d+\))?:\s*(PASS|HOLD)\b", posted_body, re.MULTILINE):
            print("FATAL: Posted comment missing '### Decision(...)' — verdict corrupt", file=sys.stderr)
            sys.exit(1)

    return html_url


def create_issue(token: str, repo: str, title: str, body: str, labels: list[str]) -> str:
    payload = {"title": title, "body": body}
    if labels:
        payload["labels"] = labels
    r = requests.post(
        f"https://api.github.com/repos/{repo}/issues",
        headers=_headers(token),
        json=payload,
    )
    r.raise_for_status()
    issue_number = r.json()["number"]
    html_url = r.json()["html_url"]

    # Verify issue created
    v = requests.get(
        f"https://api.github.com/repos/{repo}/issues/{issue_number}",
        headers=_headers(token),
    )
    if v.status_code != 200:
        print(f"FATAL: Issue creation verification failed. Issue {issue_number} not found (HTTP {v.status_code})", file=sys.stderr)
        sys.exit(1)

    return html_url


def update_issue(token: str, repo: str, issue: int, body: str) -> str:
    r = requests.patch(
        f"https://api.github.com/repos/{repo}/issues/{issue}",
        headers=_headers(token),
        json={"body": body},
    )
    r.raise_for_status()
    html_url = r.json()["html_url"]

    # Verify update landed
    v = requests.get(
        f"https://api.github.com/repos/{repo}/issues/{issue}",
        headers=_headers(token),
    )
    if v.status_code != 200:
        print(f"FATAL: Issue update verification failed. Issue {issue} not found (HTTP {v.status_code})", file=sys.stderr)
        sys.exit(1)
    if v.json().get("body", "").strip() != body.strip():
        print(f"FATAL: Issue body mismatch after update — content did not persist", file=sys.stderr)
        sys.exit(1)

    return html_url


def main():
    parser = argparse.ArgumentParser(description="Post to GitHub as app identity")
    parser.add_argument("agent", choices=["tdd", "qa"], help="Agent identity")
    parser.add_argument("action", choices=["comment", "create-issue", "update-issue"], help="Action to perform")
    parser.add_argument("repo", help="OWNER/REPO")
    parser.add_argument("issue", nargs="?", help="Issue number (required for comment and update-issue)")
    parser.add_argument("body_file", nargs="?", help="Path to markdown file")
    parser.add_argument("--body", help="Inline body text")
    parser.add_argument("--title", help="Issue title (required for create-issue)")
    parser.add_argument("--label", action="append", default=[], help="Label (repeatable)")
    parser.add_argument(
        "--keys-dir",
        type=Path,
        default=default_keys_dir(),
        help="Directory containing .pem keys",
    )
    args = parser.parse_args()

    # For create-issue, argparse would consume body_file as the optional 'issue' positional.
    # Detect and reassign: if action is create-issue and issue is set but body_file is not,
    # the value in issue is actually the body_file path.
    if args.action == "create-issue" and args.issue is not None and args.body_file is None:
        args.body_file = args.issue
        args.issue = None

    # Convert issue to int for actions that require it
    if args.issue is not None:
        try:
            args.issue = int(args.issue)
        except (ValueError, TypeError):
            print(f"FATAL: issue must be an integer, got: {args.issue!r}", file=sys.stderr)
            sys.exit(2)

    # Read body
    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8", errors="replace")
    elif args.body:
        body = args.body
    else:
        body = sys.stdin.read()

    if not body.strip():
        print("FATAL: empty body", file=sys.stderr)
        sys.exit(1)

    token = get_token(args.agent, args.keys_dir)

    if args.action == "comment":
        if args.issue is None:
            print("FATAL: comment action requires ISSUE_NUMBER", file=sys.stderr)
            sys.exit(2)
        url = post_comment(token, args.repo, args.issue, body, agent_id=args.agent)
    elif args.action == "create-issue":
        if not args.title:
            print("FATAL: create-issue requires --title", file=sys.stderr)
            sys.exit(2)
        url = create_issue(token, args.repo, args.title, body, args.label)
    elif args.action == "update-issue":
        if args.issue is None:
            print("FATAL: update-issue action requires ISSUE_NUMBER", file=sys.stderr)
            sys.exit(2)
        url = update_issue(token, args.repo, args.issue, body)

    print(url)


if __name__ == "__main__":
    main()
