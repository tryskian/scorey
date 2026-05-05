from __future__ import annotations

import argparse
import shutil
import sys
import termios
import threading
import tty
from collections.abc import Callable
from pathlib import Path
from typing import TextIO

from scorey.config import load_settings, require_openai_api_key
from scorey.eval_db import (
    counts,
    default_eval_db_path,
    get_output,
    init_db,
    judge_output,
    list_outputs,
    list_review_sample,
)
from scorey.eval_gates import (
    BETA_1_DISPLAY_NAME,
    beta_1_pass_pairs,
    evaluate_beta_1,
    summarise_gate_results,
)
from scorey.eval_sampling import (
    LOCAL_SAMPLE_PATTERNS,
    explicit_local_sample_pairs,
    format_local_sample_pair,
    sample_local_eval_outputs,
)
from scorey.pipeline import (
    build_local_round_state,
    build_round_state,
    choose_scorey_pick,
    compose_round,
)

APP_PICKS: tuple[str, ...] = ("rock", "paper", "scissors")
APP_BANNER_LINES: tuple[str, ...] = (
    "scorey",
    "scorey keeps the score.",
    "sorry. you already lost.",
)
APP_PICK_PROMPT = "pick your loser [arrow keys]:"
APP_PICK_PROMPT_FALLBACK = "pick your loser:"
APP_CONTINUE_PROMPT = "another round [y/n]?"
APP_LOADING_TEXT = "scorey is deciding why you lost"
ANSI_CURSOR_HIDE = "\x1b[?25l"
ANSI_CURSOR_SHOW = "\x1b[?25h"


class AppExit(Exception):
    """Exit the interactive app loop cleanly."""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scorey")
    parser.add_argument(
        "--local",
        action="store_true",
        help="Use deterministic local fixture rounds instead of live generation.",
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    subparsers.add_parser("app", help="Open the interactive Scorey app.")

    play_parser = subparsers.add_parser("play", help="Play one Scorey round.")
    play_parser.add_argument("pick")

    subparsers.add_parser("eval-init", help="Initialize the local eval database.")

    eval_list_parser = subparsers.add_parser(
        "eval-list",
        help="List recent rows from the local eval database.",
    )
    eval_list_parser.add_argument("--limit", type=int, default=20)
    eval_list_parser.add_argument(
        "--verdict",
        choices=("pass", "fail", "pending"),
        default=None,
        help="Optionally filter rows by current human verdict.",
    )

    eval_beta_1_parser = subparsers.add_parser(
        "eval-beta-1",
        help="Run the Beta 1.0 picks gate against recent eval rows.",
    )
    eval_beta_1_parser.add_argument("--limit", type=int, default=20)

    eval_review_sample_parser = subparsers.add_parser(
        "eval-review-sample",
        help="List a stratified pending review sample.",
    )
    eval_review_sample_parser.add_argument("--limit", type=int, default=12)

    eval_judge_parser = subparsers.add_parser(
        "eval-judge",
        help="Record a human verdict for one eval output.",
    )
    eval_judge_parser.add_argument("output_id", type=int)
    eval_judge_parser.add_argument("verdict", choices=("pass", "fail"))
    eval_judge_parser.add_argument(
        "--note",
        required=True,
        help="Short human note explaining the verdict.",
    )

    eval_sample_local_parser = subparsers.add_parser(
        "eval-sample-local",
        help="Record deterministic local rounds into the eval database.",
    )
    eval_sample_local_group = eval_sample_local_parser.add_mutually_exclusive_group(
        required=True
    )
    eval_sample_local_group.add_argument("--count", type=int)
    eval_sample_local_group.add_argument("--duration-seconds", type=float)
    eval_sample_local_parser.add_argument("--interval-seconds", type=float, default=0.0)
    eval_sample_local_parser.add_argument(
        "--pattern",
        choices=LOCAL_SAMPLE_PATTERNS,
        default=None,
        help="Choose a named deterministic local pair cycle.",
    )
    eval_sample_local_parser.add_argument(
        "--pair",
        action="append",
        default=[],
        metavar="SCOREY_PICK,USER_PICK",
        help="Repeat to provide an explicit local pair cycle in scorey/user order.",
    )

    return parser


def print_app_header(output_fn: Callable[[str], None] = print) -> None:
    width = shutil.get_terminal_size(fallback=(80, 24)).columns
    for line in APP_BANNER_LINES:
        if width >= len(line):
            output_fn(line)
        else:
            output_fn(line[:width])
    output_fn("")


def read_selector_key(input_stream: TextIO | None = None) -> str:
    stream = sys.stdin if input_stream is None else input_stream
    if not stream.isatty():
        raise RuntimeError("Selector key reading requires a TTY.")

    fileno = stream.fileno()
    original = termios.tcgetattr(fileno)
    try:
        tty.setraw(fileno)
        first = stream.read(1)
        if first in ("\r", "\n"):
            return "ENTER"
        if first == "\x1b":
            second = stream.read(1)
            if second == "[":
                third = stream.read(1)
                if third == "A":
                    return "UP"
                if third == "B":
                    return "DOWN"
            return "ESC"
        return first
    finally:
        termios.tcsetattr(fileno, termios.TCSADRAIN, original)


def clear_screen(output_stream: TextIO | None = None) -> None:
    stream = sys.stdout if output_stream is None else output_stream
    stream.write("\033[2J\033[H")
    stream.flush()


def render_pick_selector(
    selected_index: int, output_stream: TextIO | None = None
) -> None:
    stream = sys.stdout if output_stream is None else output_stream
    clear_screen(stream)
    print_app_header(lambda line: print(line, file=stream))
    print(APP_PICK_PROMPT, file=stream)
    for index, pick in enumerate(APP_PICKS):
        prefix = ">" if index == selected_index else " "
        print(f"{prefix} {pick}", file=stream)
    print("\n[enter] select, [esc] exit", file=stream)
    stream.flush()


def prompt_for_pick_fallback(
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> str:
    input_fn = input if input_fn is None else input_fn
    output_fn = print if output_fn is None else output_fn
    while True:
        output_fn(APP_PICK_PROMPT_FALLBACK)
        for index, pick in enumerate(APP_PICKS, start=1):
            output_fn(f"{index}. {pick}")
        raw = input_fn("> ").strip().lower()
        if raw in {"esc", "exit", "quit"}:
            raise AppExit
        if raw in APP_PICKS:
            return raw
        if raw in {"1", "2", "3"}:
            return APP_PICKS[int(raw) - 1]
        output_fn("pick rock, paper, or scissors.")


def prompt_for_pick_selector() -> str:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return prompt_for_pick_fallback()

    selected_index = 0
    sys.stdout.write(ANSI_CURSOR_HIDE)
    sys.stdout.flush()
    try:
        while True:
            render_pick_selector(selected_index)
            key = read_selector_key()
            if key == "UP":
                selected_index = (selected_index - 1) % len(APP_PICKS)
            elif key == "DOWN":
                selected_index = (selected_index + 1) % len(APP_PICKS)
            elif key == "ENTER":
                return APP_PICKS[selected_index]
            elif key == "ESC":
                raise AppExit
    finally:
        sys.stdout.write(ANSI_CURSOR_SHOW)
        sys.stdout.flush()
        clear_screen()


def prompt_to_continue(
    input_fn: Callable[[str], str] | None = None,
    output_fn: Callable[[str], None] | None = None,
) -> bool:
    input_fn = input if input_fn is None else input_fn
    output_fn = print if output_fn is None else output_fn
    while True:
        answer = input_fn(f"{APP_CONTINUE_PROMPT} ").strip().lower()
        if answer in {"y", "yes"}:
            return True
        if answer in {"n", "no", ""}:
            output_fn("")
            return False
        output_fn("answer y or n.")


def run_with_loading(task: Callable[[], str]) -> str:
    result: dict[str, str] = {}
    error: dict[str, BaseException] = {}
    done = threading.Event()

    def worker() -> None:
        try:
            result["value"] = task()
        except BaseException as exc:  # pragma: no cover - exercised in live mode
            error["value"] = exc
        finally:
            done.set()

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    spinner = "|/-\\"
    index = 0
    while not done.wait(0.08):
        sys.stdout.write(f"\r{APP_LOADING_TEXT} {spinner[index % len(spinner)]}")
        sys.stdout.flush()
        index += 1

    sys.stdout.write("\r" + (" " * (len(APP_LOADING_TEXT) + 3)) + "\r")
    sys.stdout.flush()

    if "value" in error:
        raise error["value"]
    return result["value"]


def build_round_text(
    user_pick: str,
    *,
    local: bool,
    scorey_score: int,
) -> str:
    if local:
        return compose_round(
            build_local_round_state(user_pick, scorey_score=scorey_score)
        )

    settings = load_settings()
    require_openai_api_key()
    scorey_pick = choose_scorey_pick(user_pick)

    from scorey.agent import generate_live_round_fields

    fields = generate_live_round_fields(
        settings,
        user_pick,
        scorey_pick,
        "same-pick" if user_pick == scorey_pick else "cross-object",
    )
    round_state = build_round_state(
        user_pick,
        scorey_pick,
        fields,
        scorey_score=scorey_score,
    )
    return compose_round(round_state)


def command_app(local: bool) -> int:
    scorey_score = 0
    try:
        while True:
            user_pick = prompt_for_pick_selector()
            scorey_score += 1
            if local:
                round_text = build_round_text(
                    user_pick,
                    local=True,
                    scorey_score=scorey_score,
                )
            else:

                def live_round_task(
                    current_pick: str = user_pick,
                    current_score: int = scorey_score,
                ) -> str:
                    return build_round_text(
                        current_pick,
                        local=False,
                        scorey_score=current_score,
                    )

                round_text = run_with_loading(live_round_task)

            print_app_header()
            print(f"> {user_pick}\n")
            print(round_text)
            print("")
            if not prompt_to_continue():
                return 0
    except AppExit:
        print("")
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


def command_play(user_pick: str, local: bool) -> int:
    try:
        if local:
            round_text = build_round_text(user_pick, local=True, scorey_score=1)
        else:
            round_text = build_round_text(user_pick, local=False, scorey_score=1)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(round_text)
    return 0


def command_eval_init() -> int:
    db_path = default_eval_db_path()
    init_db(db_path)
    print(f"initialized eval db: {db_path}")
    return 0


def _format_scorey_user_pair(scorey_pick: str, user_pick: str) -> str:
    return f"scorey={scorey_pick} user={user_pick}"


def _format_eval_row(db_path: Path, row_id: int) -> str:
    row = get_output(db_path, row_id)
    verdict = row["current_verdict"] or "pending"
    lines = [
        (
            f"[{row['id']}] "
            f"{_format_scorey_user_pair(row['scorey_pick'], row['user_pick'])} "
            f"({row['route_family']}, {row['source_mode']}, {verdict})"
        ),
        f"model: {row['model']}",
        row["round_text"],
    ]
    note = row["current_note"]
    if note:
        lines.append(f"note: {note}")
    return "\n".join(lines)


def command_eval_list(limit: int, verdict: str | None) -> int:
    db_path = default_eval_db_path()
    init_db(db_path)
    summary = counts(db_path)
    print(
        "eval counts: "
        f"total={summary['total']} pass={summary['pass']} "
        f"fail={summary['fail']} pending={summary['pending']}"
    )

    rows = list_outputs(db_path, limit=limit, verdict=verdict)
    if not rows:
        print("no eval outputs yet.")
        return 0

    print("")
    for index, row in enumerate(rows):
        if index > 0:
            print("")
        print(_format_eval_row(db_path, int(row["id"])))
    return 0


def command_eval_beta_1(limit: int) -> int:
    db_path = default_eval_db_path()
    init_db(db_path)
    rows = list_outputs(db_path, limit=limit)

    print(f"{BETA_1_DISPLAY_NAME} gate: picks only (`scorey_pick`, `user_pick`)")
    print("pass pairs:")
    for scorey_pick, user_pick in beta_1_pass_pairs():
        print(f"- {scorey_pick} / {user_pick}")
    print("fail: all other scorey/user pick pairs.")

    if not rows:
        print("")
        print("no eval outputs yet.")
        return 0

    results = [
        evaluate_beta_1(
            user_pick=str(row["user_pick"]),
            scorey_pick=str(row["scorey_pick"]),
        )
        for row in rows
    ]
    summary = summarise_gate_results(results)
    print("")
    print(
        f"{BETA_1_DISPLAY_NAME} counts: "
        f"total={summary['total']} pass={summary['pass']} fail={summary['fail']}"
    )
    print("")
    for index, (row, result) in enumerate(zip(rows, results, strict=True)):
        if index > 0:
            print("")
        human_verdict = row["current_verdict"] or "pending"
        print(
            f"[{row['id']}] {result.verdict} "
            f"{_format_scorey_user_pair(result.scorey_pick, result.user_pick)} "
            f"({row['route_family']}, {row['source_mode']}, human={human_verdict})"
        )
        print(f"reason: {result.reason}")
        print(f"model: {row['model']}")
        print(row["round_text"])
        if row["current_note"]:
            print(f"human note: {row['current_note']}")
    return 0


def command_eval_review_sample(limit: int) -> int:
    db_path = default_eval_db_path()
    init_db(db_path)
    summary = counts(db_path)
    print(
        "eval counts: "
        f"total={summary['total']} pass={summary['pass']} "
        f"fail={summary['fail']} pending={summary['pending']}"
    )
    print(f"review sample: newest pending row per model/pair (limit={limit})")

    rows = list_review_sample(db_path, limit=limit)
    if not rows:
        print("")
        print("no pending eval outputs.")
        return 0

    print("")
    for index, row in enumerate(rows):
        if index > 0:
            print("")
        print(_format_eval_row(db_path, int(row["id"])))
    return 0


def command_eval_judge(output_id: int, verdict: str, note: str) -> int:
    db_path = default_eval_db_path()
    init_db(db_path)
    try:
        judge_output(db_path, output_id, verdict, note)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"judged output {output_id}: {verdict}")
    print(f"note: {note}")
    print("")
    print(_format_eval_row(db_path, output_id))
    return 0


def command_eval_sample_local(
    *,
    count: int | None,
    duration_seconds: float | None,
    interval_seconds: float,
    pattern: str | None,
    pair_specs: list[str],
) -> int:
    try:
        pair_cycle = (
            explicit_local_sample_pairs(tuple(pair_specs)) if pair_specs else None
        )
        summary = sample_local_eval_outputs(
            count=count,
            duration_seconds=duration_seconds,
            interval_seconds=interval_seconds,
            pattern=pattern or "baseline",
            pair_cycle=pair_cycle,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    mode_label = (
        f"count={count}"
        if count is not None
        else f"duration_seconds={duration_seconds:g}"
    )
    db_path = default_eval_db_path()
    print(f"local eval sample complete: {mode_label}")
    if pair_specs:
        print(
            "pairs="
            + " ".join(format_local_sample_pair(pair) for pair in pair_cycle or ())
        )
    else:
        print(f"pattern={pattern or 'baseline'}")
    print(
        f"recorded={summary.recorded} "
        f"beta_1_pass={summary.beta_1_pass} beta_1_fail={summary.beta_1_fail}"
    )
    print(f"elapsed_seconds={summary.elapsed_seconds:.2f}")
    if summary.first_output_id is not None and summary.last_output_id is not None:
        print(
            f"output_ids={summary.first_output_id}-{summary.last_output_id} "
            f"db={db_path}"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command in (None, "app"):
        return command_app(local=args.local)
    if args.command == "play":
        return command_play(args.pick, local=args.local)
    if args.command == "eval-init":
        return command_eval_init()
    if args.command == "eval-list":
        return command_eval_list(args.limit, args.verdict)
    if args.command == "eval-beta-1":
        return command_eval_beta_1(args.limit)
    if args.command == "eval-review-sample":
        return command_eval_review_sample(args.limit)
    if args.command == "eval-judge":
        return command_eval_judge(args.output_id, args.verdict, args.note)
    if args.command == "eval-sample-local":
        return command_eval_sample_local(
            count=args.count,
            duration_seconds=args.duration_seconds,
            interval_seconds=args.interval_seconds,
            pattern=args.pattern,
            pair_specs=args.pair,
        )
    parser.print_help()
    return 1
