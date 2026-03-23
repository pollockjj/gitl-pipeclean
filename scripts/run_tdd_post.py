#!/usr/bin/env python3
"""TDD posting runner — resolves Python interpreter and delegates to post_as_app.py.

Usage:
    run_tdd_post.py comment OWNER/REPO ISSUE_NUMBER BODY_FILE
    run_tdd_post.py update-issue OWNER/REPO ISSUE_NUMBER BODY_FILE
    run_tdd_post.py create-issue OWNER/REPO --title "Title" BODY_FILE
    run_tdd_post.py create-issue OWNER/REPO --title "Title" --label tdd-plan BODY_FILE

Resolves a Python interpreter with jwt/cryptography/requests available, then
delegates to scripts/post_as_app.py as tdd identity. Exits non-zero on any failure.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from run_qa_gate import FatalError, resolve_post_python


def main() -> int:
    try:
        post_python = resolve_post_python()
        post_script = ROOT / "scripts" / "post_as_app.py"
        command = [post_python, str(post_script), "tdd"] + sys.argv[1:]
        result = subprocess.run(command, check=False)
        return result.returncode
    except FatalError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
