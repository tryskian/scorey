#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[start] starting morning routine in: $ROOT_DIR"
echo "[start] 1/7 workspace context"
printf 'repo root: %s\n' "$ROOT_DIR"
printf 'branch: %s\n' "$(git branch --show-current)"
git status --short --branch

echo "[start] 2/7 doctor-env"
make --no-print-directory doctor-env

echo "[start] 3/7 start-runtime-check"
make --no-print-directory start-runtime-check

echo "[start] 4/7 caffeinate"
make --no-print-directory caffeinate

echo "[start] 5/7 caffeinate-status"
make --no-print-directory caffeinate-status

echo "[start] 6/7 session-status"
make --no-print-directory session-status

echo "[start] 7/7 STOP"
echo "[start] read these docs:"
echo "  - README.md"
echo "  - docs/governance/CHARTER.md"
echo "  - docs/governance/DECISIONS.md"
echo "  - docs/runtime/RUNBOOK.md"
echo "  - docs/runtime/ARCHITECTURE.md"
echo "  - docs/governance/SESSION_HANDOFF.md"
echo "[start] before any repo action:"
echo "  1. give the startup read"
echo "  2. name exactly one active kernel"
echo "  3. do not branch, search, or edit until that is stated"
