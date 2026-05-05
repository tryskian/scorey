# Beta Eval 2.0: Focused Object Lanes

## Question

Can one object stay stable when Scorey is forced to show it as both a win and a loss?

## Short Answer

Yes for both completed lanes so far. The focused pair-cycle method held cleanly for rock and then for paper across full local long runs.

## Eval Shape

`Beta Eval 2.0` keeps the `Beta Eval 1.0` routing gate, but changes the sampling architecture.

Instead of asking for the full pass table at once, it isolates one object through an explicit local pair cycle.

Final completed lane:

- `scissors,rock`
- `paper,scissors`

Read in `scorey_pick,user_pick` order, this means:

- scissors appears as Scorey's winning object
- scissors appears as the user's losing object

What stays out of scope:

- full-table coverage
- prose quality
- tone
- scoreboard claim

## Current Signal

The first focused rock lane produced:

- `3568` rows in the one-hour run
- `3580` total `local-explicit-pair-cycle-batch` rows including the short validation sample
- `1790` rows of `rock/paper`
- `1790` rows of `scissors/rock`

The newest readback on that lane remained all-pass under `Beta 1.0`.

The focused paper lane then produced:

- `3579` rows in the long run after the short validation sample
- `1790` rows of `paper/scissors`
- `1789` rows of `rock/paper`
- the newest readback on that lane remained all-pass under `Beta 1.0`

The first stratified human judgment sweep then started on top of the local rows:

- `12` pass
- `0` fail
- one reviewed row per model/pair sample across:
  - `local-fixture-batch`
  - `local-beta-1-coverage-batch`
  - `local-explicit-pair-cycle-batch`

So the important result here is not just balance. It is that the repo now has a clean way to isolate one object lane without inventing a new named sampler every time.

## What Changed Next

All three object lanes are now complete on the local path.

The next useful move is to expand the human judgment sample and then decide whether Scorey earns a wider prose, tone, or scoreboard-focused eval lane.
