# Beta Eval 2.0: Focused Object Lanes

## Question

Can one object stay stable when Scorey is forced to show it as both a win and a loss?

## Short Answer

Yes for the first rock lane. The focused pair-cycle lane held cleanly across a full hour, and the paper lane is now the active follow-on run.

## Eval Shape

`Beta Eval 2.0` keeps the `Beta Eval 1.0` routing gate, but changes the sampling architecture.

Instead of asking for the full pass table at once, it isolates one object through an explicit local pair cycle.

Current lane:

- `paper,scissors`
- `rock,paper`

Read in `scorey_pick,user_pick` order, this means:

- paper appears as Scorey's winning object
- paper appears as the user's losing object

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

The active paper lane has already cleared a short validation sample:

- `12` rows recorded
- `12` pass
- `0` fail
- evenly split across:
  - `paper/scissors`
  - `rock/paper`

So the important result here is not just balance. It is that the repo now has a clean way to isolate one object lane without inventing a new named sampler every time.

## What Changed Next

The obvious next move is to repeat the same lane shape for:

- `scissors`

Once the paper lane settles, repeat the same shape for `scissors`.

Only after those object lanes are stable should Scorey widen into prose, tone, or scoreboard-focused eval lanes.
