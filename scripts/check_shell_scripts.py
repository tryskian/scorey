from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXECUTABLE_STRICT_MODE = {
    "#!/usr/bin/env bash": "set -euo pipefail",
    "#!/usr/bin/env sh": "set -eu",
}


def tracked_shell_scripts() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "scripts"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(path) for path in result.stdout.splitlines() if path.endswith(".sh")]


def check_script(path: Path) -> list[str]:
    text = (REPO_ROOT / path).read_text(encoding="utf-8")
    lines = text.splitlines()
    failures: list[str] = []

    if "\r\n" in text:
        failures.append("uses CRLF line endings")

    if not lines:
        return ["is empty"]

    shebang = lines[0]
    if shebang not in EXECUTABLE_STRICT_MODE:
        failures.append(
            "uses unsupported shebang "
            f"{shebang!r}; expected one of {sorted(EXECUTABLE_STRICT_MODE)}"
        )
        return failures

    expected_strict_mode = EXECUTABLE_STRICT_MODE[shebang]
    if len(lines) < 2 or lines[1] != expected_strict_mode:
        failures.append(
            f"does not enable strict mode on line 2 ({expected_strict_mode!r})"
        )

    return failures


def main() -> int:
    failures: list[str] = []
    shell_scripts = tracked_shell_scripts()

    if not shell_scripts:
        failures.append("no tracked shell scripts found under scripts/")

    for path in shell_scripts:
        for failure in check_script(path):
            failures.append(f"{path}: {failure}")

    if failures:
        print("shell-script-contracts: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"shell-script-contracts: PASS ({len(shell_scripts)} scripts checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
