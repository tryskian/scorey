from __future__ import annotations

import argparse
import select
import shutil
import sys
import termios
import threading
import time
import tty
from collections.abc import Callable
from pathlib import Path
from typing import TextIO

from scorey.config import Settings, load_settings, require_openai_api_key
from scorey.eval_db import (
    archive_failure_disposition_for_lens,
    archive_output_for_lens,
    counts,
    default_eval_db_path,
    get_output,
    init_db,
    judge_output,
    judge_output_for_lens,
    lens_counts,
    lens_failure_disposition_counts,
    list_lens_failure_disposition_sample,
    list_lens_review_sample,
    list_outputs,
    list_review_sample,
    record_failure_disposition_for_lens,
)
from scorey.eval_gates import (
    RESEARCH_BETA_1_DISPLAY_NAME,
    evaluate_research_beta_1,
    research_beta_1_pass_pairs,
    summarise_gate_results,
)
from scorey.eval_sampling import (
    LOCAL_SAMPLE_PATTERNS,
    explicit_local_sample_pairs,
    explicit_user_pick_cycle,
    format_local_sample_pair,
    sample_live_eval_outputs,
    sample_local_eval_outputs,
)
from scorey.pipeline import (
    RoundState,
    build_local_round_state,
    build_round_state,
    choose_scorey_pick,
    compose_round,
    pick_verb,
)

APP_PICKS: tuple[str, ...] = ("rock", "paper", "scissors")
APP_BANNER_INNER_WIDTH = 62
APP_BANNER_TITLE = "SCOREY RESEARCH BETA 3.0"
APP_BANNER_TAGLINE = "scorey keeps the score and you've already lost."
APP_BANNER_REPO = "github.com/tryskian/scorey"
APP_BANNER_REPO_URL = "https://github.com/tryskian/scorey"
APP_BANNER_BOX_WIDTH = APP_BANNER_INNER_WIDTH + 2
APP_BANNER_STACKED_WIDTH = len(APP_BANNER_TAGLINE)
APP_BANNER_MINIMAL_WIDTH = len(APP_BANNER_REPO)
APP_BANNER_MINIMAL_TITLE = "scorey research beta 3.0"
APP_BANNER_MINIMAL_TAGLINE_LINES: tuple[str, ...] = (
    "scorey keeps the score and",
    "you've already lost.",
    "sorry.",
)
APP_ROUND_PROMPT = "let's play!"
APP_PICK_PROMPT = "you:"
APP_PICK_PROMPT_FALLBACK = "pick your loser:"
APP_CONTINUE_PROMPT = "another round [y/n]?"
APP_LOADING_TEXT = "scorey is deciding why you lost"
APP_ME_PLACEHOLDER = "[inactive until you press enter]"
APP_PLAY_HINT = "press enter to play or esc to exit"
APP_REPLAY_HINT = "press enter to play again or esc to exit"
APP_CONTINUE_DELAY_SECONDS = 0.25
ANSI_RESET = "\x1b[0m"
ANSI_BOLD = "\x1b[1m"
ANSI_REPO_ACCENT = "\x1b[38;5;117m"
ANSI_MUTED = "\x1b[38;5;245m"
ANSI_CURSOR_HIDE = "\x1b[?25l"
ANSI_CURSOR_SHOW = "\x1b[?25h"
ESC_SEQUENCE_TIMEOUT_SECONDS = 0.03


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

    research_beta_1_parser = subparsers.add_parser(
        "research-beta-1",
        aliases=["eval-beta-1"],
        help="Run the Research Beta 1.0 picks gate against recent eval rows.",
    )
    research_beta_1_parser.add_argument("--limit", type=int, default=20)

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

    eval_tone_sample_parser = subparsers.add_parser(
        "eval-tone-sample",
        help="List a stratified pending tone review sample from live route-pass rows.",
    )
    eval_tone_sample_parser.add_argument("--limit", type=int, default=12)
    eval_tone_sample_parser.add_argument(
        "--pick",
        action="append",
        default=[],
        choices=APP_PICKS,
        metavar="USER_PICK",
        help="Repeat to narrow the tone sample to one or more user picks.",
    )

    eval_tone_judge_parser = subparsers.add_parser(
        "eval-tone-judge",
        help="Record a tone verdict for one eval output.",
    )
    eval_tone_judge_parser.add_argument("output_id", type=int)
    eval_tone_judge_parser.add_argument("verdict", choices=("pass", "fail"))
    eval_tone_judge_parser.add_argument(
        "--note",
        required=True,
        help="Short tone note explaining the verdict.",
    )

    eval_tone_archive_parser = subparsers.add_parser(
        "eval-tone-archive",
        help="Archive one pending tone row out of the active review surface.",
    )
    eval_tone_archive_parser.add_argument("output_id", type=int)
    eval_tone_archive_parser.add_argument(
        "--note",
        required=True,
        help="Short note explaining why the pending tone row is being archived.",
    )

    eval_tone_disposition_sample_parser = subparsers.add_parser(
        "eval-tone-disposition-sample",
        help="List a stratified tone-fail sample that still needs RETAIN or EVICT.",
    )
    eval_tone_disposition_sample_parser.add_argument("--limit", type=int, default=12)
    eval_tone_disposition_sample_parser.add_argument(
        "--pick",
        action="append",
        default=[],
        choices=APP_PICKS,
        metavar="USER_PICK",
        help=(
            "Repeat to narrow the tone-fail disposition sample to one or more "
            "user picks."
        ),
    )

    eval_tone_disposition_archive_parser = subparsers.add_parser(
        "eval-tone-disposition-archive",
        help="Archive one failed tone row out of the active disposition surface.",
    )
    eval_tone_disposition_archive_parser.add_argument("output_id", type=int)
    eval_tone_disposition_archive_parser.add_argument(
        "--note",
        required=True,
        help="Short note explaining why the failed tone row is being archived.",
    )

    eval_tone_dispose_parser = subparsers.add_parser(
        "eval-tone-dispose",
        help="Record RETAIN or EVICT for one failed tone row.",
    )
    eval_tone_dispose_parser.add_argument("output_id", type=int)
    eval_tone_dispose_parser.add_argument("disposition", choices=("retain", "evict"))
    eval_tone_dispose_parser.add_argument(
        "--note",
        required=True,
        help="Short note explaining the failure disposition.",
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

    eval_sample_live_parser = subparsers.add_parser(
        "eval-sample-live",
        help="Record live API rounds into the eval database.",
    )
    eval_sample_live_group = eval_sample_live_parser.add_mutually_exclusive_group(
        required=True
    )
    eval_sample_live_group.add_argument("--count", type=int)
    eval_sample_live_group.add_argument("--duration-seconds", type=float)
    eval_sample_live_parser.add_argument("--interval-seconds", type=float, default=0.0)
    eval_sample_live_parser.add_argument(
        "--pick",
        action="append",
        default=[],
        metavar="USER_PICK",
        help="Repeat to provide an explicit user-pick cycle in user order.",
    )
    eval_sample_live_parser.add_argument(
        "--pair",
        action="append",
        default=[],
        metavar="SCOREY_PICK,USER_PICK",
        help="Repeat to provide an explicit live pair cycle in scorey/user order.",
    )

    return parser


def build_banner_lines(style_active: bool = False) -> tuple[str, ...]:
    def hyperlink(text: str, url: str) -> str:
        return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"

    def styled_repo(text: str, url: str) -> str:
        if not style_active:
            return text
        linked = hyperlink(text, url)
        return f"{ANSI_BOLD}{ANSI_REPO_ACCENT}{linked}{ANSI_RESET}"

    def boxed(text: str = "", *, link_url: str | None = None) -> str:
        if link_url is None:
            return f"│{text.center(APP_BANNER_INNER_WIDTH)}│"

        left_padding = max(0, (APP_BANNER_INNER_WIDTH - len(text)) // 2)
        right_padding = max(0, APP_BANNER_INNER_WIDTH - len(text) - left_padding)
        repo_text = styled_repo(text, link_url)
        return f"│{' ' * left_padding}{repo_text}{' ' * right_padding}│"

    return (
        f"┌{'─' * APP_BANNER_INNER_WIDTH}┐",
        boxed(APP_BANNER_TITLE),
        boxed(APP_BANNER_TAGLINE),
        boxed(),
        boxed(APP_BANNER_REPO, link_url=APP_BANNER_REPO_URL),
        f"└{'─' * APP_BANNER_INNER_WIDTH}┘",
    )


def build_stacked_banner_lines(style_active: bool = False) -> tuple[str, ...]:
    repo_line = APP_BANNER_REPO
    if style_active:
        repo_line = (
            f"{ANSI_BOLD}{ANSI_REPO_ACCENT}"
            f"\033]8;;{APP_BANNER_REPO_URL}\033\\{APP_BANNER_REPO}\033]8;;\033\\"
            f"{ANSI_RESET}"
        )
    return (
        APP_BANNER_TITLE,
        APP_BANNER_TAGLINE,
        repo_line,
    )


def build_minimal_banner_lines(style_active: bool = False) -> tuple[str, ...]:
    repo_line = APP_BANNER_REPO
    if style_active:
        repo_line = (
            f"{ANSI_BOLD}{ANSI_REPO_ACCENT}"
            f"\033]8;;{APP_BANNER_REPO_URL}\033\\{APP_BANNER_REPO}\033]8;;\033\\"
            f"{ANSI_RESET}"
        )
    return (
        APP_BANNER_MINIMAL_TITLE,
        *APP_BANNER_MINIMAL_TAGLINE_LINES,
        repo_line,
    )


def choose_banner_lines(
    terminal_width: int | None,
    style_active: bool = False,
) -> tuple[str, ...]:
    if terminal_width is None or terminal_width >= APP_BANNER_BOX_WIDTH:
        return build_banner_lines(style_active=style_active)
    if terminal_width >= APP_BANNER_STACKED_WIDTH:
        return build_stacked_banner_lines(style_active=style_active)
    if terminal_width >= APP_BANNER_MINIMAL_WIDTH:
        return build_minimal_banner_lines(style_active=style_active)
    return (
        APP_BANNER_MINIMAL_TITLE,
        *APP_BANNER_MINIMAL_TAGLINE_LINES,
    )


def print_app_header(output_stream: TextIO | None = None) -> None:
    stream = sys.stdout if output_stream is None else output_stream
    width = shutil.get_terminal_size(fallback=(80, 24)).columns
    style_active = bool(getattr(stream, "isatty", lambda: False)())
    for line in choose_banner_lines(width, style_active=style_active):
        print(line, file=stream)
    print("", file=stream)


def format_pick_option(pick: str, selected: bool, style_active: bool = False) -> str:
    line = f"> {pick}" if selected else f"  {pick}"
    if selected and style_active:
        return f"{ANSI_BOLD}{line}{ANSI_RESET}"
    return line


def format_muted(text: str, style_active: bool = False) -> str:
    if not style_active:
        return text
    return f"{ANSI_MUTED}{text}{ANSI_RESET}"


def build_ruling_line(round_state: RoundState) -> str:
    return (
        f"my {round_state.scorey_pick} beats your {round_state.user_pick} because my "
        f"{round_state.scorey_pick} {pick_verb(round_state.scorey_pick)} "
        f"{round_state.winning_state} and your {round_state.user_pick} "
        f"{pick_verb(round_state.user_pick)} {round_state.worse_state}."
    )


def build_score_line(round_state: RoundState) -> str:
    return f"me: {round_state.scorey_score}, you: {round_state.scoreboard_claim}"


def build_round_scene_lines(
    selected_index: int,
    *,
    revealed_scorey_pick: str | None = None,
    loading_frame: str | None = None,
    round_state: RoundState | None = None,
    style_active: bool = False,
) -> list[str]:
    lines = [
        APP_ROUND_PROMPT,
        "",
        APP_PICK_PROMPT,
    ]
    lines.extend(
        format_pick_option(pick, index == selected_index, style_active=style_active)
        for index, pick in enumerate(APP_PICKS)
    )
    lines.append("")

    lines.append("me:")
    if revealed_scorey_pick is None:
        lines.append(format_muted(f"  {APP_ME_PLACEHOLDER}", style_active=style_active))
    else:
        me_line = f"> {revealed_scorey_pick}"
        if style_active:
            me_line = f"{ANSI_BOLD}{me_line}{ANSI_RESET}"
        lines.append(me_line)

    lines.append("")

    if round_state is not None:
        lines.append(f"> {build_ruling_line(round_state)}")
    elif loading_frame is not None:
        lines.append(f"> {loading_frame} {APP_LOADING_TEXT}")
    else:
        lines.append("")

    lines.append("")

    if round_state is not None:
        lines.append(build_score_line(round_state))
        lines.append("scorey.")
        footer = APP_REPLAY_HINT
    else:
        lines.append("")
        lines.append("")
        footer = APP_PLAY_HINT

    lines.append("")
    lines.append(format_muted(footer, style_active=style_active))
    return lines


def render_round_scene(
    selected_index: int,
    *,
    output_stream: TextIO | None = None,
    redraw: bool = False,
    revealed_scorey_pick: str | None = None,
    loading_frame: str | None = None,
    round_state: RoundState | None = None,
) -> int:
    stream = sys.stdout if output_stream is None else output_stream
    style_active = bool(getattr(stream, "isatty", lambda: False)())
    lines = build_round_scene_lines(
        selected_index,
        revealed_scorey_pick=revealed_scorey_pick,
        loading_frame=loading_frame,
        round_state=round_state,
        style_active=style_active,
    )
    if redraw:
        stream.write(f"\x1b[{len(lines)}F")
    for line in lines:
        stream.write(f"\r{ANSI_RESET}\x1b[2K")
        stream.write(f"{line}\n")
    stream.flush()
    return len(lines)


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
            second = _read_optional_tty_byte(stream)
            if second is None:
                return "ESC"
            if second == "[":
                third = _read_optional_tty_byte(stream)
                if third == "A":
                    return "UP"
                if third == "B":
                    return "DOWN"
            return "ESC"
        return first
    finally:
        termios.tcsetattr(fileno, termios.TCSADRAIN, original)


def _read_optional_tty_byte(
    stream: TextIO,
    *,
    timeout_seconds: float = ESC_SEQUENCE_TIMEOUT_SECONDS,
) -> str | None:
    ready, _, _ = select.select([stream.fileno()], [], [], timeout_seconds)
    if not ready:
        return None
    value = stream.read(1)
    if value == "":
        return None
    return value


def clear_screen(output_stream: TextIO | None = None) -> None:
    stream = sys.stdout if output_stream is None else output_stream
    stream.write("\033[2J\033[H")
    stream.flush()


def render_pick_selector(
    selected_index: int, output_stream: TextIO | None = None
) -> None:
    stream = sys.stdout if output_stream is None else output_stream
    render_round_scene(selected_index, output_stream=stream)


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


def prompt_for_pick_selector() -> tuple[int, str]:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        pick = prompt_for_pick_fallback()
        return APP_PICKS.index(pick), pick

    selected_index = 0
    sys.stdout.write(ANSI_CURSOR_HIDE)
    sys.stdout.flush()
    try:
        while True:
            render_round_scene(selected_index)
            key = read_selector_key()
            if key == "UP":
                selected_index = (selected_index - 1) % len(APP_PICKS)
                render_round_scene(selected_index, redraw=True)
            elif key == "DOWN":
                selected_index = (selected_index + 1) % len(APP_PICKS)
                render_round_scene(selected_index, redraw=True)
            elif key == "ENTER":
                return selected_index, APP_PICKS[selected_index]
            elif key == "ESC":
                raise AppExit
    finally:
        sys.stdout.write(ANSI_CURSOR_SHOW)
        sys.stdout.flush()


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


def prompt_to_continue_selector(
    read_key_fn: Callable[[], str] | None = None,
    output_stream: TextIO | None = None,
) -> bool:
    del output_stream
    read_key_fn = read_selector_key if read_key_fn is None else read_key_fn
    while True:
        key = read_key_fn()
        if key == "ENTER":
            return True
        if key == "ESC":
            return False


def run_with_loading(
    task: Callable[[], RoundState],
    *,
    output_stream: TextIO | None = None,
    render_frame: Callable[[str], None] | None = None,
) -> RoundState:
    stream = sys.stdout if output_stream is None else output_stream
    result: dict[str, RoundState] = {}
    error: dict[str, BaseException] = {}
    stop = threading.Event()
    frames = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴")

    def animate() -> None:
        frame_index = 0
        while not stop.is_set():
            frame = frames[frame_index % len(frames)]
            if render_frame is None:
                stream.write(f"\r\x1b[2K{frame}")
                stream.flush()
            else:
                render_frame(frame)
            frame_index += 1
            if stop.wait(0.14):
                break
        if render_frame is None:
            stream.write("\r\x1b[2K")
            stream.flush()

    def worker() -> None:
        try:
            result["value"] = task()
        except BaseException as exc:  # pragma: no cover - exercised in live mode
            error["value"] = exc
        finally:
            stop.set()

    thread = threading.Thread(target=animate, daemon=True)
    thread.start()
    worker_thread = threading.Thread(target=worker, daemon=True)
    worker_thread.start()
    worker_thread.join()
    thread.join()

    if "value" in error:
        raise error["value"]
    return result["value"]


def build_live_round_state(
    user_pick: str,
    *,
    settings: Settings,
    scorey_pick: str,
    scorey_score: int,
) -> RoundState:
    route_family = "same-pick" if user_pick == scorey_pick else "cross-object"

    from scorey.agent import generate_live_round_fields

    fields = generate_live_round_fields(
        settings,
        user_pick,
        scorey_pick,
        route_family,
    )
    return build_round_state(
        user_pick,
        scorey_pick,
        fields,
        scorey_score=scorey_score,
    )


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
    use_selector = sys.stdin.isatty() and sys.stdout.isatty()
    try:
        while True:
            if use_selector:
                clear_screen(sys.stdout)
                print_app_header(sys.stdout)
                selected_index, user_pick = prompt_for_pick_selector()
            else:
                selected_index = 0
                user_pick = prompt_for_pick_fallback()
            scorey_score += 1
            if local:
                round_state = build_local_round_state(
                    user_pick,
                    scorey_score=scorey_score,
                )
            else:
                settings = load_settings()
                require_openai_api_key()
                scorey_pick = choose_scorey_pick(user_pick)

                def live_round_task(
                    current_pick: str = user_pick,
                    current_score: int = scorey_score,
                    current_scorey_pick: str = scorey_pick,
                    current_settings: Settings = settings,
                ) -> RoundState:
                    return build_live_round_state(
                        current_pick,
                        settings=current_settings,
                        scorey_pick=current_scorey_pick,
                        scorey_score=current_score,
                    )

                def render_loading_frame(
                    frame: str,
                    current_index: int = selected_index,
                    current_scorey_pick: str = scorey_pick,
                ) -> None:
                    render_round_scene(
                        current_index,
                        output_stream=sys.stdout,
                        redraw=True,
                        revealed_scorey_pick=current_scorey_pick,
                        loading_frame=frame,
                    )

                if use_selector:
                    round_state = run_with_loading(
                        live_round_task,
                        output_stream=sys.stdout,
                        render_frame=render_loading_frame,
                    )
                else:
                    round_state = live_round_task()

            if use_selector:
                render_round_scene(
                    selected_index,
                    output_stream=sys.stdout,
                    redraw=True,
                    revealed_scorey_pick=round_state.scorey_pick,
                    round_state=round_state,
                )
                if not prompt_to_continue_selector(output_stream=sys.stdout):
                    print("")
                    return 0
                time.sleep(APP_CONTINUE_DELAY_SECONDS)
            else:
                print("")
                print(compose_round(round_state))
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
    verdict = str(row["current_verdict"])
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
        if summary["total"] == 0:
            print("no eval outputs yet.")
        elif verdict is None:
            print("no eval outputs found.")
        else:
            print(f"no {verdict} eval outputs.")
        return 0

    print("")
    for index, row in enumerate(rows):
        if index > 0:
            print("")
        print(_format_eval_row(db_path, int(row["id"])))
    return 0


def command_research_beta_1(limit: int) -> int:
    db_path = default_eval_db_path()
    init_db(db_path)
    rows = list_outputs(db_path, limit=limit)

    print(
        f"{RESEARCH_BETA_1_DISPLAY_NAME} gate: picks only (`scorey_pick`, `user_pick`)"
    )
    print("pass pairs:")
    for scorey_pick, user_pick in research_beta_1_pass_pairs():
        print(f"- {scorey_pick} / {user_pick}")
    print("fail: all other scorey/user pick pairs.")

    if not rows:
        print("")
        print("no eval outputs yet.")
        return 0

    results = [
        evaluate_research_beta_1(
            user_pick=str(row["user_pick"]),
            scorey_pick=str(row["scorey_pick"]),
        )
        for row in rows
    ]
    summary = summarise_gate_results(results)
    print("")
    print(
        f"{RESEARCH_BETA_1_DISPLAY_NAME} counts: "
        f"total={summary['total']} pass={summary['pass']} fail={summary['fail']}"
    )
    print("")
    for index, (row, result) in enumerate(zip(rows, results, strict=True)):
        if index > 0:
            print("")
        human_verdict = str(row["current_verdict"])
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


def command_eval_tone_sample(limit: int, user_picks: list[str]) -> int:
    db_path = default_eval_db_path()
    init_db(db_path)
    resolved_user_picks = tuple(user_picks) if user_picks else None
    summary = lens_counts(
        db_path,
        lens="tone",
        source_mode="live",
        user_picks=resolved_user_picks,
    )
    archived_suffix = f" archived={summary['archived']}" if summary["archived"] else ""
    print(
        "tone counts: "
        f"total={summary['total']} pass={summary['pass']} "
        f"fail={summary['fail']} pending={summary['pending']}{archived_suffix}"
    )
    print(f"tone sample: newest pending live row per model/pair (limit={limit})")
    if resolved_user_picks is not None:
        print(f"user_picks={' '.join(resolved_user_picks)}")

    rows = list_lens_review_sample(
        db_path,
        lens="tone",
        source_mode="live",
        limit=limit,
        user_picks=resolved_user_picks,
    )
    if not rows:
        print("")
        print("no pending tone eval outputs.")
        return 0

    print("")
    for index, row in enumerate(rows):
        if index > 0:
            print("")
        print(_format_eval_row(db_path, int(row["id"])))
    return 0


def command_eval_tone_judge(output_id: int, verdict: str, note: str) -> int:
    db_path = default_eval_db_path()
    init_db(db_path)
    try:
        judge_output_for_lens(
            db_path,
            output_id,
            lens="tone",
            verdict=verdict,
            note=note,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"judged tone output {output_id}: {verdict}")
    print(f"note: {note}")
    print("")
    print(_format_eval_row(db_path, output_id))
    return 0


def command_eval_tone_archive(output_id: int, note: str) -> int:
    db_path = default_eval_db_path()
    init_db(db_path)
    try:
        archive_output_for_lens(
            db_path,
            output_id,
            lens="tone",
            note=note,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"archived tone output {output_id}")
    print(f"note: {note}")
    print("")
    print(_format_eval_row(db_path, output_id))
    return 0


def command_eval_tone_disposition_sample(limit: int, user_picks: list[str]) -> int:
    db_path = default_eval_db_path()
    init_db(db_path)
    resolved_user_picks = tuple(user_picks) if user_picks else None
    summary = lens_failure_disposition_counts(
        db_path,
        lens="tone",
        source_mode="live",
        user_picks=resolved_user_picks,
    )
    print(
        "tone fail disposition counts: "
        f"total={summary['total']} retain={summary['retain']} "
        f"evict={summary['evict']} pending={summary['pending']}"
        + (f" archived={summary['archived']}" if summary["archived"] else "")
    )
    print(
        "tone fail disposition sample: "
        f"newest failed live row per model/pair (limit={limit})"
    )
    if resolved_user_picks is not None:
        print(f"user_picks={' '.join(resolved_user_picks)}")

    rows = list_lens_failure_disposition_sample(
        db_path,
        lens="tone",
        source_mode="live",
        limit=limit,
        user_picks=resolved_user_picks,
    )
    if not rows:
        print("")
        print("no pending tone failure dispositions.")
        return 0

    print("")
    for index, row in enumerate(rows):
        if index > 0:
            print("")
        print(_format_eval_row(db_path, int(row["id"])))
    return 0


def command_eval_tone_dispose(output_id: int, disposition: str, note: str) -> int:
    db_path = default_eval_db_path()
    init_db(db_path)
    try:
        record_failure_disposition_for_lens(
            db_path,
            output_id,
            lens="tone",
            disposition=disposition,
            note=note,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"recorded tone disposition for output {output_id}: {disposition}")
    print(f"note: {note}")
    print("")
    print(_format_eval_row(db_path, output_id))
    return 0


def command_eval_tone_disposition_archive(output_id: int, note: str) -> int:
    db_path = default_eval_db_path()
    init_db(db_path)
    try:
        archive_failure_disposition_for_lens(
            db_path,
            output_id,
            lens="tone",
            note=note,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"archived tone disposition output {output_id}")
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
        "research_beta_1_pass="
        f"{summary.research_beta_1_pass} "
        "research_beta_1_fail="
        f"{summary.research_beta_1_fail}"
    )
    print(f"elapsed_seconds={summary.elapsed_seconds:.2f}")
    if summary.first_output_id is not None and summary.last_output_id is not None:
        print(
            f"output_ids={summary.first_output_id}-{summary.last_output_id} "
            f"db={db_path}"
        )
    return 0


def command_eval_sample_live(
    *,
    count: int | None,
    duration_seconds: float | None,
    interval_seconds: float,
    user_picks: list[str],
    pair_specs: list[str],
) -> int:
    try:
        if user_picks and pair_specs:
            raise ValueError("Provide either --pick or --pair, not both.")
        user_pick_cycle = (
            explicit_user_pick_cycle(tuple(user_picks)) if user_picks else None
        )
        pair_cycle = (
            explicit_local_sample_pairs(tuple(pair_specs)) if pair_specs else None
        )
        summary = sample_live_eval_outputs(
            count=count,
            duration_seconds=duration_seconds,
            interval_seconds=interval_seconds,
            user_pick_cycle=user_pick_cycle,
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
    print(f"live eval sample complete: {mode_label}")
    if pair_cycle is not None:
        print(
            "pairs=" + " ".join(format_local_sample_pair(pair) for pair in pair_cycle)
        )
    elif user_pick_cycle is not None:
        print("user_picks=" + " ".join(user_pick_cycle))
    else:
        print("user_picks=rock paper scissors")
    print(
        f"recorded={summary.recorded} "
        "research_beta_1_pass="
        f"{summary.research_beta_1_pass} "
        "research_beta_1_fail="
        f"{summary.research_beta_1_fail}"
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
    if args.command in {"research-beta-1", "eval-beta-1"}:
        return command_research_beta_1(args.limit)
    if args.command == "eval-review-sample":
        return command_eval_review_sample(args.limit)
    if args.command == "eval-judge":
        return command_eval_judge(args.output_id, args.verdict, args.note)
    if args.command == "eval-tone-sample":
        return command_eval_tone_sample(args.limit, args.pick)
    if args.command == "eval-tone-judge":
        return command_eval_tone_judge(args.output_id, args.verdict, args.note)
    if args.command == "eval-tone-archive":
        return command_eval_tone_archive(args.output_id, args.note)
    if args.command == "eval-tone-disposition-sample":
        return command_eval_tone_disposition_sample(args.limit, args.pick)
    if args.command == "eval-tone-disposition-archive":
        return command_eval_tone_disposition_archive(args.output_id, args.note)
    if args.command == "eval-tone-dispose":
        return command_eval_tone_dispose(
            args.output_id,
            args.disposition,
            args.note,
        )
    if args.command == "eval-sample-local":
        return command_eval_sample_local(
            count=args.count,
            duration_seconds=args.duration_seconds,
            interval_seconds=args.interval_seconds,
            pattern=args.pattern,
            pair_specs=args.pair,
        )
    if args.command == "eval-sample-live":
        return command_eval_sample_live(
            count=args.count,
            duration_seconds=args.duration_seconds,
            interval_seconds=args.interval_seconds,
            user_picks=args.pick,
            pair_specs=args.pair,
        )
    parser.print_help()
    return 1
