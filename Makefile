PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin
PIP := $(shell if [ -x "$(BIN)/pip" ]; then echo "$(BIN)/pip"; else echo "$(PYTHON) -m pip"; fi)
PY := $(shell if [ -x "$(BIN)/python" ]; then echo "$(BIN)/python"; else echo "$(PYTHON)"; fi)
PICK ?= rock
LOCAL ?=
EVAL_LIMIT ?= 10
EVAL_VERDICT ?=
EVAL_COUNT ?= 30
EVAL_DURATION_SECONDS ?=
EVAL_INTERVAL_SECONDS ?= 0
EVAL_PATTERN ?= baseline
EVAL_PAIRS ?=
EVAL_USER_PICKS ?=
OUTPUT_ID ?=
VERDICT ?=
DISPOSITION ?=
NOTE ?=
OPENAI_LIMITS_URL ?= https://platform.openai.com/settings/organization/limits
OPENAI_USAGE_URL ?= https://platform.openai.com/settings/organization/usage
OPENAI_BILLING_URL ?= https://platform.openai.com/settings/organization/billing/overview
CAFFEINATE_PID_FILE ?= /tmp/scorey-caffeinate.pid
CAFFEINATE_LOG ?= /tmp/scorey-caffeinate.log
CAFFEINATE_CMD ?= /usr/bin/caffeinate -d -i -m
PIP_AUDIT_ARGS ?=
RUNTIME_ARGS = $(if $(filter 1 true yes,$(LOCAL)),--local,)

.PHONY: install env venv doctor-env path-leak-check path-leak-audit-local session-status test test-cov lint format-check format typecheck precommit-install precommit-run prepush-run check package-check app play rock paper scissors eval-init eval-list eval-judge eval-tone-sample eval-tone-judge eval-tone-archive eval-tone-disposition-sample eval-tone-disposition-archive eval-tone-dispose research-beta1 eval-beta1 eval-sample-local eval-sample-live open-limits open-usage open-billing open-cost-console caffeinate decaffeinate caffeinate-status decaffeinate-status start end rituals start-runtime-check end-preflight end-docs-check end-runtime-check end-git-check clean
.PHONY: lint-docs package-install-check python-security-check security-checks
.PHONY: eval-review-sample

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -e ".[dev]"

env venv:
	@test -d "$(VENV)" || (echo "Missing .venv. Run make install." && exit 1)
	@echo "Opening shell in $(VENV)"
	@. "$(BIN)/activate" && exec "$$SHELL" -i

doctor-env:
	$(PY) ./scripts/doctor_env.py

path-leak-check:
	$(PY) ./scripts/path_leak_check.py --scope tracked

path-leak-audit-local:
	$(PY) ./scripts/path_leak_check.py --scope local

test:
	PYTHONPATH=src $(PY) -m pytest

test-cov:
	PYTHONPATH=src $(PY) -m pytest --cov --cov-report=term-missing

lint:
	$(PY) -m ruff check scripts src tests

format-check:
	$(PY) -m ruff format --check scripts src tests

format:
	$(PY) -m ruff format scripts src tests

typecheck:
	PYTHONPATH=src $(PY) -m mypy scripts src tests

lint-docs:
	npx --yes markdownlint-cli2 README.md docs/**/*.md

precommit-install:
	$(PY) -m pre_commit install --install-hooks --hook-type pre-commit --hook-type pre-push

precommit-run:
	$(PY) -m pre_commit run --all-files

prepush-run:
	$(PY) -m pre_commit run --all-files --hook-stage pre-push

session-status:
	@set -eu; \
	echo "== Scorey Session Status =="; \
	echo "repo: $$(pwd)"; \
	if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then \
		echo "branch: $$(git branch --show-current)"; \
		if git diff --quiet --ignore-submodules HEAD -- && [ -z "$$(git ls-files --others --exclude-standard)" ]; then \
			echo "worktree: clean"; \
		else \
			echo "worktree: dirty"; \
		fi; \
	else \
		echo "branch: not a git repo"; \
		echo "worktree: unknown"; \
	fi; \
	if [ -f "docs/governance/SESSION_HANDOFF.md" ]; then \
		echo "handoff: docs/governance/SESSION_HANDOFF.md"; \
	fi; \
		if [ -f "pyproject.toml" ]; then \
			echo "package: pyproject.toml"; \
		fi; \
		if [ -f "$(CAFFEINATE_PID_FILE)" ]; then \
			PID=$$(cat "$(CAFFEINATE_PID_FILE)" 2>/dev/null || true); \
			if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
				echo "caffeinate: on (PID $$PID)"; \
			else \
				echo "caffeinate: stale pid file"; \
			fi; \
		else \
			echo "caffeinate: off"; \
		fi; \
	PYTHONPATH=src $(PY) ./scripts/check_end_runtime_state.py

check:
	$(MAKE) --no-print-directory format-check
	$(MAKE) --no-print-directory lint
	$(PY) -m compileall scripts src tests
	$(MAKE) --no-print-directory typecheck
	$(MAKE) --no-print-directory test-cov
	git diff --check

package-check:
	PYTHONPATH=src $(PY) -m build

package-install-check:
	$(PY) -m pip install --no-deps -e .
	$(PY) -c "import importlib; importlib.import_module('scorey'); importlib.import_module('scorey.main')"

python-security-check:
	$(PY) -m pip_audit $(PIP_AUDIT_ARGS)

security-checks: python-security-check

app:
	PYTHONPATH=src $(PY) -m scorey $(RUNTIME_ARGS)

play:
	PYTHONPATH=src $(PY) -m scorey $(RUNTIME_ARGS) play $(PICK)

rock:
	$(MAKE) --no-print-directory play PICK=rock LOCAL="$(LOCAL)"

paper:
	$(MAKE) --no-print-directory play PICK=paper LOCAL="$(LOCAL)"

scissors:
	$(MAKE) --no-print-directory play PICK=scissors LOCAL="$(LOCAL)"

eval-init:
	PYTHONPATH=src $(PY) -m scorey eval-init

eval-list:
	PYTHONPATH=src $(PY) -m scorey eval-list --limit $(EVAL_LIMIT) $(if $(EVAL_VERDICT),--verdict $(EVAL_VERDICT),)

eval-review-sample:
	PYTHONPATH=src $(PY) -m scorey eval-review-sample --limit $(EVAL_LIMIT)

eval-judge:
	PYTHONPATH=src $(PY) -m scorey eval-judge $(OUTPUT_ID) $(VERDICT) --note "$(NOTE)"

eval-tone-sample:
	PYTHONPATH=src $(PY) -m scorey eval-tone-sample --limit $(EVAL_LIMIT) $(foreach pick,$(EVAL_USER_PICKS),--pick $(pick))

eval-tone-judge:
	PYTHONPATH=src $(PY) -m scorey eval-tone-judge $(OUTPUT_ID) $(VERDICT) --note "$(NOTE)"

eval-tone-archive:
	PYTHONPATH=src $(PY) -m scorey eval-tone-archive $(OUTPUT_ID) --note "$(NOTE)"

eval-tone-disposition-sample:
	PYTHONPATH=src $(PY) -m scorey eval-tone-disposition-sample --limit $(EVAL_LIMIT) $(foreach pick,$(EVAL_USER_PICKS),--pick $(pick))

eval-tone-disposition-archive:
	PYTHONPATH=src $(PY) -m scorey eval-tone-disposition-archive $(OUTPUT_ID) --note "$(NOTE)"

eval-tone-dispose:
	PYTHONPATH=src $(PY) -m scorey eval-tone-dispose $(OUTPUT_ID) $(DISPOSITION) --note "$(NOTE)"

research-beta1:
	PYTHONPATH=src $(PY) -m scorey research-beta-1 --limit $(EVAL_LIMIT)

eval-beta1:
	$(MAKE) --no-print-directory research-beta1 EVAL_LIMIT=$(EVAL_LIMIT)

eval-sample-local:
	PYTHONPATH=src $(PY) -m scorey eval-sample-local $(if $(EVAL_DURATION_SECONDS),--duration-seconds $(EVAL_DURATION_SECONDS),--count $(EVAL_COUNT)) --interval-seconds $(EVAL_INTERVAL_SECONDS) $(if $(strip $(EVAL_PAIRS)),$(foreach pair,$(EVAL_PAIRS),--pair $(pair)),--pattern $(EVAL_PATTERN))

eval-sample-live:
	PYTHONPATH=src $(PY) -m scorey eval-sample-live $(if $(EVAL_DURATION_SECONDS),--duration-seconds $(EVAL_DURATION_SECONDS),--count $(EVAL_COUNT)) --interval-seconds $(EVAL_INTERVAL_SECONDS) $(if $(strip $(EVAL_PAIRS)),$(foreach pair,$(EVAL_PAIRS),--pair $(pair)),$(foreach pick,$(EVAL_USER_PICKS),--pick $(pick)))

open-limits:
	@set -eu; \
	URL="$(OPENAI_LIMITS_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "OpenAI limits URL: $$URL"

open-usage:
	@set -eu; \
	URL="$(OPENAI_USAGE_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "OpenAI usage URL: $$URL"

open-billing:
	@set -eu; \
	URL="$(OPENAI_BILLING_URL)"; \
	if command -v open >/dev/null 2>&1; then \
		open "$$URL"; \
	elif command -v xdg-open >/dev/null 2>&1; then \
		xdg-open "$$URL" >/dev/null 2>&1 || true; \
	else \
		echo "Open this URL in your browser: $$URL"; \
	fi; \
	echo "OpenAI billing URL: $$URL"

open-cost-console:
	@set -eu; \
	$(MAKE) --no-print-directory open-limits; \
	$(MAKE) --no-print-directory open-usage; \
	$(MAKE) --no-print-directory open-billing

caffeinate:
	@set -eu; \
	if [ "$$(uname -s)" != "Darwin" ]; then \
		echo "caffeinate is macOS-only; skipping."; \
		exit 0; \
	fi; \
	if [ -f "$(CAFFEINATE_PID_FILE)" ]; then \
		PID=$$(cat "$(CAFFEINATE_PID_FILE)" 2>/dev/null || true); \
		if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
			echo "caffeinate already running (PID $$PID)."; \
			exit 0; \
		fi; \
		rm -f "$(CAFFEINATE_PID_FILE)"; \
	fi; \
	nohup $(CAFFEINATE_CMD) >"$(CAFFEINATE_LOG)" 2>&1 & \
	PID=$$!; \
	echo "$$PID" >"$(CAFFEINATE_PID_FILE)"; \
	sleep 0.1; \
	if kill -0 "$$PID" 2>/dev/null; then \
		echo "caffeinate started (PID $$PID)."; \
	else \
		rm -f "$(CAFFEINATE_PID_FILE)"; \
		echo "Failed to start caffeinate."; \
		exit 1; \
	fi

decaffeinate:
	@set -eu; \
	if [ "$$(uname -s)" != "Darwin" ]; then \
		echo "caffeinate is macOS-only; skipping."; \
		exit 0; \
	fi; \
	if [ ! -f "$(CAFFEINATE_PID_FILE)" ]; then \
		echo "No managed caffeinate PID file found."; \
		exit 0; \
	fi; \
	PID=$$(cat "$(CAFFEINATE_PID_FILE)" 2>/dev/null || true); \
	if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
		kill "$$PID"; \
		sleep 0.1; \
		echo "caffeinate stopped (PID $$PID)."; \
	else \
		echo "Stale PID file found; cleaning up."; \
	fi; \
	rm -f "$(CAFFEINATE_PID_FILE)"

caffeinate-status:
	@set -eu; \
	if [ "$$(uname -s)" != "Darwin" ]; then \
		echo "caffeinate status is only available on macOS."; \
		exit 0; \
	fi; \
	if [ -f "$(CAFFEINATE_PID_FILE)" ]; then \
		PID=$$(cat "$(CAFFEINATE_PID_FILE)" 2>/dev/null || true); \
		if [ -n "$$PID" ] && kill -0 "$$PID" 2>/dev/null; then \
			echo "Managed caffeinate: RUNNING (PID $$PID)."; \
		else \
			echo "Managed caffeinate: STALE PID file."; \
		fi; \
	else \
		echo "Managed caffeinate: OFF."; \
		EXISTING_PID=$$(pgrep -f "^/usr/bin/caffeinate -d -i -m( |$$)" | head -n 1 || true); \
		if [ -n "$$EXISTING_PID" ]; then \
			echo "Unmanaged caffeinate detected (PID $$EXISTING_PID); not owned by this repo."; \
		fi; \
	fi

decaffeinate-status: caffeinate-status

start:
	bash ./scripts/start_of_day_routine.sh

rituals:
	@cat docs/runtime/START_END_REFERENCE.md

end:
	./scripts/end_of_day_routine.sh

end-preflight:
	end_SKIP_GIT_CHECK=1 ./scripts/end_of_day_routine.sh

end-docs-check:
	$(PY) ./scripts/check_end_docs.py

start-runtime-check:
	PYTHONPATH=src $(PY) ./scripts/check_end_runtime_state.py --start-strict

end-runtime-check:
	PYTHONPATH=src $(PY) ./scripts/check_end_runtime_state.py --strict

end-git-check:
	bash ./scripts/check_end_git_clean.sh

clean:
	rm -rf $(VENV) .coverage .mypy_cache .pytest_cache .ruff_cache htmlcov coverage.xml scripts/__pycache__ src/scorey/__pycache__ tests/__pycache__ build dist src/*.egg-info
