from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text()


def assert_make_target(makefile: str, target: str) -> None:
    assert re.search(rf"(?m)^{re.escape(target)}:", makefile), target


def test_makefile_exposes_local_ci_and_closeout_targets() -> None:
    makefile = read("Makefile")

    for target in (
        "lint-docs",
        "scripts-check",
        "package-install-check",
        "python-security-check",
        "security-checks",
    ):
        assert_make_target(makefile, target)


def test_end_routine_uses_make_targets() -> None:
    script = read("scripts/end_of_day_routine.sh")

    for command in (
        "make --no-print-directory lint-docs",
        "make --no-print-directory scripts-check",
        "make --no-print-directory package-check",
        "make --no-print-directory package-install-check",
        "make --no-print-directory security-checks",
        "make --no-print-directory end-runtime-check",
        "make --no-print-directory session-status",
    ):
        assert command in script


def test_repo_lifecycle_leaves_external_power_control_unchanged() -> None:
    makefile = read("Makefile")
    start_script = read("scripts/start_of_day_routine.sh")
    end_script = read("scripts/end_of_day_routine.sh")

    for target in (
        "caffeinate",
        "caffeinate-status",
        "decaffeinate",
        "decaffeinate-status",
    ):
        assert not re.search(rf"(?m)^{re.escape(target)}:", makefile)

    for forbidden in (
        "CAFFEINATE_PID_FILE",
        "CAFFEINATE_LOG",
        "CAFFEINATE_CMD",
        "make --no-print-directory caffeinate",
        "make --no-print-directory decaffeinate",
    ):
        assert forbidden not in "\n".join((makefile, start_script, end_script))

    assert "[start] 1/5 workspace context" in start_script
    assert "[start] 5/5 REHYDRATE PROMPT" in start_script
    assert "TOTAL_STEPS=13" in end_script
    assert "TOTAL_STEPS=12" in end_script
    assert "[end] 12/$TOTAL_STEPS session snapshot" in end_script
    assert "[end] 13/$TOTAL_STEPS git closeout" in end_script

    active_docs = "\n".join(
        read(path)
        for path in (
            "README.md",
            "docs/governance/SESSION_HANDOFF.md",
            "docs/runtime/ARCHITECTURE.md",
            "docs/runtime/RUNBOOK.md",
            "docs/runtime/START_END_REFERENCE.md",
        )
    )
    assert not re.search(r"(?i)caffeinate|decaffeinate|wake-lock", active_docs)


def test_runtime_docs_name_the_make_targets() -> None:
    docs = "\n".join(
        read(path)
        for path in (
            "docs/runtime/RUNBOOK.md",
            "docs/runtime/START_END_REFERENCE.md",
            "docs/governance/DECISIONS.md",
        )
    )

    for command in (
        "make lint-docs",
        "make scripts-check",
        "make package-install-check",
        "make security-checks",
        "make end-runtime-check",
    ):
        assert command in docs


def test_shell_script_contract_checker_accepts_tracked_scripts() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/check_shell_scripts.py"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "shell-script-contracts: PASS" in result.stdout
    assert "scripts checked" in result.stdout
