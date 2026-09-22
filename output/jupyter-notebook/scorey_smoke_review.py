"""Read frozen smoke records; save attributed review events to a separate sidecar."""

from __future__ import annotations

import copy
import html
import json
from dataclasses import dataclass, field
from pathlib import Path

from scorey.review_store import (
    ReviewError,
    load_dataset,
    new_event,
    read_notes,
    save_notes,
)


def _merged_events(database: list[dict], sidecar: list[dict]) -> list[dict]:
    merged: dict[str, dict] = {}
    for event in [*database, *sidecar]:
        key = event["event_id"]
        if key in merged and merged[key] != event:
            raise ReviewError(f"Conflicting review event: {key}")
        merged[key] = event
    return sorted(merged.values(), key=lambda event: event["created_at"])


def _review(events: list[dict], case_id: str, author: str) -> dict[str, str]:
    values = {
        "verdict": "Pending",
        "reason": "",
        "field_or_phrase": "",
        "observation": "",
        "observation_phrase": "",
    }
    for event in events:
        if (
            event["case_id"] != case_id
            or event["author"] != author
            or event["role"] != "human"
        ):
            continue
        if event["kind"] == "judgment":
            values.update(
                verdict=event["verdict"],
                reason=event["note"],
                field_or_phrase=event["field_or_phrase"],
            )
        else:
            values.update(
                observation=event["note"],
                observation_phrase=event["field_or_phrase"],
            )
    return values


@dataclass
class SmokeReview:
    dataset: dict
    notes_path: Path
    author: str
    events: list[dict]
    sidecar_events: list[dict]
    reviews: dict[str, dict[str, str]]
    expected_revision: str | None = None
    index: int = 0
    _saved_reviews: dict[str, dict[str, str]] = field(default_factory=dict, repr=False)

    @property
    def count(self) -> int:
        return len(self.dataset["cases"])

    @property
    def current_case(self) -> dict:
        return self.dataset["cases"][self.index]

    @property
    def current_review(self) -> dict[str, str]:
        return self.reviews[self.current_case["case_id"]]

    @property
    def dirty(self) -> bool:
        return self.reviews != self._saved_reviews

    def update(self, **values: str) -> None:
        if not values.keys() <= self.current_review.keys():
            raise ReviewError("Unknown review field.")
        if any(not isinstance(value, str) for value in values.values()):
            raise ReviewError("Review fields must be text.")
        if values.get("verdict", "Pending") not in ("Pending", "PASS", "FAIL"):
            raise ReviewError("Choose Pending, PASS, or FAIL.")
        self.current_review.update(values)

    def navigate(self, delta: int) -> None:
        self.index = min(max(self.index + delta, 0), self.count - 1)


def load_review(
    db_path: Path,
    notes_path: Path,
    dataset_id: str | None = None,
    author: str = "Peanut",
) -> SmokeReview:
    """Load SQLite read-only and merge separately saved, source-bound notes."""
    if not author.strip():
        raise ReviewError("A review author is required.")
    dataset = load_dataset(Path(db_path), dataset_id)
    if not dataset["cases"]:
        raise ReviewError("This dataset has no rounds to review.")
    notes_path = Path(notes_path)
    sidecar, revision = read_notes(notes_path, dataset)
    events = _merged_events(dataset["events"], sidecar)
    reviews = {
        case["case_id"]: _review(events, case["case_id"], author)
        for case in dataset["cases"]
    }
    return SmokeReview(
        dataset,
        notes_path,
        author,
        events,
        sidecar,
        reviews,
        revision,
        _saved_reviews=copy.deepcopy(reviews),
    )


def save_review(session: SmokeReview) -> None:
    """Append changed judgments and observations; retain every previous event."""
    additions = []
    for case_id, current in session.reviews.items():
        saved = session._saved_reviews[case_id]
        for kind, fields in (
            ("judgment", ("verdict", "reason", "field_or_phrase")),
            ("observation", ("observation", "observation_phrase")),
        ):
            if all(current[key] == saved[key] for key in fields):
                continue
            if kind == "judgment":
                if current["verdict"] == "Pending":
                    raise ReviewError(
                        "Choose PASS or FAIL for a judgment. "
                        "Use Your observations to save a note without a verdict. "
                        "A saved judgment cannot be erased."
                    )
                verdict = current["verdict"]
                note, phrase = current["reason"], current["field_or_phrase"]
            else:
                verdict = None
                note, phrase = current["observation"], current["observation_phrase"]
            if kind == "observation" and not note.strip():
                raise ReviewError(
                    f"Add a {kind} note. Earlier notes remain in the history."
                )
            additions.append(
                new_event(
                    session.dataset,
                    case_id,
                    session.author,
                    kind,
                    note,
                    role="human",
                    verdict=verdict,
                    field_or_phrase=phrase,
                    source="notebook",
                )
            )
    if not additions:
        return
    combined = [*session.sidecar_events, *additions]
    revision = save_notes(
        session.notes_path, session.dataset, combined, session.expected_revision
    )
    session.sidecar_events = combined
    session.expected_revision = revision
    session.events = _merged_events(session.dataset["events"], combined)
    session._saved_reviews = copy.deepcopy(session.reviews)


def _text(value: object) -> str:
    return html.escape(str(value if value is not None else "not recorded"))


def _pre(value: str) -> str:
    return '<div class="scorey-wrapped">' + html.escape(value) + "</div>"


def _json(value: object) -> str:
    return _pre(json.dumps(value, ensure_ascii=False, indent=2))


def _event_html(event: dict) -> str:
    verdict = " · " + event["verdict"] if event.get("verdict") else ""
    phrase = event.get("field_or_phrase", "")
    return (
        '<article class="scorey-event"><strong>'
        + _text(event["author"])
        + " · "
        + _text(event["role"])
        + " · "
        + _text(event["kind"] + verdict)
        + "</strong>"
        + (_pre("Field or phrase: " + phrase) if phrase else "")
        + _pre(event["note"])
        + "<small>"
        + _text(event["created_at"])
        + " · Source: "
        + _text(event["source"])
        + "</small></article>"
    )


def round_html(dataset: dict, case: dict) -> str:
    """Render source text and recorded measures without assigning quality labels."""
    receipt, condition = case["receipt"], case["case"]
    usage = receipt.get("usage") or {}
    route = receipt.get("route_check") or {}
    mechanics = receipt.get("mechanical_checks") or {}
    mechanical = {True: "Checks passed", False: "Checks failed"}.get(
        mechanics.get("ok"), "not recorded"
    )
    route_label = {"pass": "Valid", "fail": "Invalid"}.get(
        route.get("verdict"), "not recorded"
    )
    normalized = receipt.get("normalized_round") or {}
    return (
        '<div class="scorey-round">'
        + _pre(receipt.get("round_text") or "No complete round was recorded.")
        + '</div><dl class="scorey-measures">'
        + "<dt>Picks</dt><dd>Scorey: "
        + _text(condition["scorey_pick"])
        + " · You: "
        + _text(condition["user_pick"])
        + "</dd>"
        + "<dt>Family / score</dt><dd>"
        + _text(condition["route_family"])
        + " · "
        + _text(normalized.get("scorey_score", condition.get("starting_score")))
        + "</dd><dt>Attempt</dt><dd>"
        + _text(receipt.get("status"))
        + " · "
        + _text(receipt.get("elapsed_seconds"))
        + " seconds</dd>"
        + "<dt>Tokens</dt><dd>"
        + _text(usage.get("input_tokens"))
        + " input · "
        + _text(usage.get("output_tokens"))
        + " output · "
        + _text(usage.get("total_tokens"))
        + " total · "
        + _text((usage.get("output_tokens_details") or {}).get("reasoning_tokens"))
        + " reasoning</dd><dt>Automated route check</dt><dd>"
        + route_label
        + " · "
        + _text(route.get("reason"))
        + "</dd><dt>Automated mechanical checks</dt><dd>"
        + mechanical
        + "</dd></dl>"
        + "<p>These checks do not judge Scorey's voice or response quality.</p>"
        + "<p><strong>Requested model:</strong> "
        + _text(dataset["manifest"]["settings"].get("model"))
        + " · <strong>Returned model:</strong> "
        + _text((receipt.get("returned_settings") or {}).get("model"))
        + "</p>"
    )


def details_html(dataset: dict, case: dict) -> str:
    receipt = case["receipt"]
    requested = copy.deepcopy(dataset["manifest"]["settings"])
    for key in ("temperature", "max_output_tokens"):
        requested.setdefault(key, "not set in the frozen configuration")
    return (
        "<h4>Requested settings</h4>"
        + _json(requested)
        + "<h4>Returned settings</h4>"
        + _json(receipt.get("returned_settings"))
        + "<h4>Case purpose</h4>"
        + _pre(case["case"].get("purpose", ""))
        + "<h4>Frozen instructions</h4>"
        + _pre(dataset["manifest"]["instructions"])
        + "<h4>Frozen case prompt</h4>"
        + _pre(case["case"].get("prompt", ""))
        + "<h4>Source identity</h4>"
        + _json(
            {
                "dataset_id": dataset["dataset_id"],
                "case_id": case["case_id"],
                "response_id": receipt.get("response_id"),
                "manifest_sha256": dataset["manifest_sha256"],
                "criteria_id": dataset["criteria_id"],
                "criteria_sha256": dataset["criteria_sha256"],
                "receipt_sha256": case["receipt_sha256"],
                "request_sha256": case["request_sha256"],
                "response_sha256": case["response_sha256"],
            }
        )
        + "<h4>Original receipt</h4>"
        + _json(receipt)
    )


def build_workbench(session: SmokeReview):
    """Build a wrapped, one-round reader with independent human observations."""
    try:
        import ipywidgets as widgets
    except ImportError as exc:
        raise ReviewError(
            "Install the notebook requirements and restart the kernel."
        ) from exc

    position, reading, assistant, history, details, status = (
        widgets.HTML() for _ in range(6)
    )
    previous = widgets.Button(description="Previous", icon="arrow-left")
    following = widgets.Button(description="Next", icon="arrow-right")
    save = widgets.Button(
        description="Save all reviews", button_style="primary", icon="save"
    )
    verdict = widgets.Dropdown(
        options=("Pending", "PASS", "FAIL"),
        description="Your verdict",
        style={"description_width": "initial"},
    )
    controls = {"verdict": verdict}
    for key, label in (
        ("reason", "Your reason (optional)"),
        ("field_or_phrase", "Judged field or phrase"),
        ("observation", "Your observations"),
        ("observation_phrase", "Observed field or phrase"),
    ):
        constructor = widgets.Text if "phrase" in key else widgets.Textarea
        controls[key] = constructor(
            description=label,
            style={"description_width": "initial"},
            layout=widgets.Layout(width="100%"),
        )
    controls[
        "observation"
    ].placeholder = "An observation can be saved without a verdict."
    controls[
        "reason"
    ].placeholder = "Optional. You don't need to repeat a shared issue for every round."
    loading = False
    originals: dict[str, str] = {}
    displayed: dict[str, str] = {}

    def update_status(message: str | None = None) -> None:
        if message is None:
            message = (
                "Unsaved edits. Previous and Next keep them in this session."
                if session.dirty
                else "Saved review events are in the separate notes file."
                if session.expected_revision
                else "Source records loaded. Save review keeps new notes separately."
            )
        status.value = (
            '<div role="status" aria-live="polite">' + _text(message) + "</div>"
        )

    def render() -> None:
        nonlocal loading, originals, displayed
        loading = True
        case_id = session.current_case["case_id"]
        position.value = (
            f"<strong>Round {session.index + 1} of {session.count} · "
            f"{_text(case_id)}</strong>"
            + "<p>Reviewing as "
            + _text(session.author)
            + " · human</p>"
        )
        reading.value = round_html(session.dataset, session.current_case)
        details.value = details_html(session.dataset, session.current_case)
        events = [event for event in session.events if event["case_id"] == case_id]
        assistant_events = [event for event in events if event["role"] == "assistant"]
        assistant.value = "<h3>Assistant notes and judgments</h3>" + (
            "".join(_event_html(event) for event in assistant_events)
            or "<p>No assistant observations or judgments recorded.</p>"
        )
        history.value = (
            "".join(_event_html(event) for event in events)
            or "<p>No saved review events for this round.</p>"
        )
        originals = dict(session.current_review)
        displayed = {
            key: value.replace("\u2028", "\n").replace("\u2029", "\n")
            for key, value in originals.items()
        }
        saved_verdict = session._saved_reviews[case_id]["verdict"]
        verdict.options = (
            ("Pending", "PASS", "FAIL")
            if saved_verdict == "Pending"
            else ("PASS", "FAIL")
        )
        for key, widget in controls.items():
            widget.value = displayed[key]
        previous.disabled = session.index == 0
        following.disabled = session.index == session.count - 1
        loading = False
        update_status()

    def changed(_change) -> None:
        if loading:
            return
        session.update(
            **{
                key: originals[key] if widget.value == displayed[key] else widget.value
                for key, widget in controls.items()
            }
        )
        update_status()

    def move(delta: int) -> None:
        session.navigate(delta)
        render()

    def persist(_button) -> None:
        try:
            save_review(session)
        except ReviewError as exc:
            update_status("Could not save: " + str(exc) + " Your edits are still here.")
        else:
            render()

    for widget in controls.values():
        widget.observe(changed, names="value")
    previous.on_click(lambda _button: move(-1))
    following.on_click(lambda _button: move(1))
    save.on_click(persist)
    criterion = widgets.HTML(
        "<strong>Frozen criterion: "
        + _text(session.dataset["criteria_id"])
        + "</strong>"
        + _pre(session.dataset["criteria_text"])
    )
    reference = widgets.Accordion(children=[criterion, details, history])
    for index, title in enumerate(
        ("Frozen review criterion", "Conditions and source", "All saved review events")
    ):
        reference.set_title(index, title)
    reference.selected_index = None
    style = widgets.HTML("""<style>
    .jp-Notebook:has(.scorey-smoke-review) { --jp-notebook-max-width:100%; }
    .scorey-smoke-review { width:100%; max-width:none; min-width:0; gap:12px;
        min-height:calc(100dvh - 290px); box-sizing:border-box;
        color:var(--jp-ui-font-color1, inherit); }
    .scorey-smoke-review .widget-html, .scorey-smoke-review .widget-html-content {
        width:100%; min-width:0; margin:0; }
    .scorey-smoke-review .scorey-wrapped { white-space:pre-wrap;
        overflow-wrap:anywhere; line-height:1.55; font-family:inherit; }
    .scorey-smoke-review .scorey-round { font-size:19px; margin:12px 0 20px; }
    .scorey-smoke-review .scorey-measures { display:grid;
        grid-template-columns:max-content minmax(0,1fr); gap:5px 18px; }
    .scorey-smoke-review dd { margin:0; overflow-wrap:anywhere; }
    .scorey-smoke-review .scorey-event { padding:10px 0;
        border-bottom:1px solid var(--jp-border-color2,#ddd); }
    .scorey-smoke-review textarea { min-height:115px; line-height:1.5!important;
        font-size:16px!important; font-family:inherit!important; }
    .scorey-smoke-review .widget-textarea, .scorey-smoke-review .widget-text {
        flex-direction:column; align-items:stretch; margin:0; }
    .scorey-smoke-review .widget-textarea > label,
    .scorey-smoke-review .widget-text > label { width:auto!important;
        text-align:left; margin:0 0 6px; }
    .scorey-smoke-review button { min-height:34px; }
    </style>""")
    panel = widgets.VBox(
        [
            style,
            position,
            widgets.HBox(
                [previous, following],
                layout=widgets.Layout(grid_gap="8px", flex_flow="row wrap"),
            ),
            reading,
            widgets.HTML(
                "<strong>Does the invented relationship make "
                "Scorey's unfair win follow?</strong>"
            ),
            reference,
            verdict,
            controls["field_or_phrase"],
            controls["reason"],
            controls["observation_phrase"],
            controls["observation"],
            save,
            status,
            assistant,
        ],
        layout=widgets.Layout(width="100%"),
    )
    panel.add_class("scorey-smoke-review")
    render()
    return panel
