from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from pathlib import Path


def _ok(message: str) -> None:
    print(f"doctor-env: OK {message}")


def _warn(message: str) -> None:
    print(f"doctor-env: WARN {message}")


def main() -> int:
    python = Path(sys.executable)
    _ok(f"python={python}")

    if shutil.which("git") is None:
        print("doctor-env: FAIL git is not available", file=sys.stderr)
        return 1
    _ok("git available")

    venv_present = Path(".venv").exists()
    if venv_present:
        _ok(".venv present")
    else:
        _warn(".venv missing (run make install when the runtime lane needs it)")

    if Path("pyproject.toml").exists():
        _ok("pyproject present")
    else:
        print("doctor-env: FAIL pyproject.toml is missing", file=sys.stderr)
        return 1

    runtime_root = Path("src/scorey")
    if runtime_root.exists():
        _ok("runtime package present")
    else:
        print("doctor-env: FAIL src/scorey is missing", file=sys.stderr)
        return 1

    handoff = Path("docs/governance/SESSION_HANDOFF.md")
    if not handoff.exists():
        print(
            "doctor-env: FAIL docs/governance/SESSION_HANDOFF.md is missing",
            file=sys.stderr,
        )
        return 1
    _ok("handoff present")

    if os.getenv("OPENAI_API_KEY"):
        _ok("OPENAI_API_KEY available for live generation")
    else:
        _warn("OPENAI_API_KEY missing (local mode still works)")

    if venv_present:
        for module_name in (
            "build",
            "mypy",
            "pre_commit",
            "pytest",
            "pytest_cov",
            "ruff",
        ):
            if importlib.util.find_spec(module_name) is None:
                print(
                    "doctor-env: FAIL "
                    f"{module_name} is not installed in the active environment",
                    file=sys.stderr,
                )
                return 1
            _ok(f"{module_name} available")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
