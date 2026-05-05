# Beta Eval 2.0: Focused Object Slices

## Question

Can one object stay stable when Scorey is forced to show it as both a win and a loss?

## Short Answer

Yes for the first rock slice. The focused pair-cycle lane held cleanly across a full hour.

## Eval Shape

`Beta Eval 2.0` keeps the `Beta Eval 1.0` routing gate, but changes the sampling architecture.

Instead of asking for the full pass table at once, it isolates one object through an explicit local pair cycle.

Current slice:

- `rock,paper`
- `scissors,rock`

Read in `scorey_pick,user_pick` order, this means:

- rock appears as Scorey's winning object
- rock appears as the user's losing object

What stays out of scope:

- full-table coverage
- prose quality
- tone
- scoreboard claim

## Current Signal

The first focused rock slice produced:

- `3568` rows in the one-hour run
- `3580` total `local-explicit-pair-cycle-batch` rows including the short validation sample
- `1790` rows of `rock/paper`
- `1790` rows of `scissors/rock`

The newest readback on that slice remained all-pass under `Beta 1.0`.

So the important result here is not just balance. It is that the repo now has a clean way to isolate one object slice without inventing a new named sampler every time.

## What Changed Next

The obvious next move is to repeat the same slice shape for:

- `paper`
- `scissors`

Only after those object slices are stable should Scorey widen into prose, tone, or scoreboard-focused eval lanes.
