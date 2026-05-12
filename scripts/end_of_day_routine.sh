#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"
TOTAL_STEPS=5

if [ "${end_SKIP_GIT_CHECK:-}" = "1" ]; then
	TOTAL_STEPS=4
fi

echo "[end] starting end-of-day routine in: $ROOT_DIR"
echo "[end] 1/$TOTAL_STEPS end-docs-check"
make --no-print-directory end-docs-check

echo "[end] 2/$TOTAL_STEPS doctor-env"
make --no-print-directory doctor-env

echo "[end] 3/$TOTAL_STEPS check"
make --no-print-directory check

echo "[end] 4/$TOTAL_STEPS session snapshot"
make --no-print-directory session-status || true

if [ "${end_SKIP_GIT_CHECK:-}" = "1" ]; then
	echo "[end] git closeout skipped (preflight only)"
else
	echo "[end] 5/$TOTAL_STEPS git closeout"
	bash ./scripts/check_end_git_clean.sh
fi

echo "[end] done"
