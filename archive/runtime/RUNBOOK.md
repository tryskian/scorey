# Runtime Runbook

## Setup

```sh
make install
```

Create `.env` from `.env.example` and set `OPENAI_API_KEY`, or export it in the
shell.

## Commands

Open the app loop:

```sh
scorey
```

The app loop opens the responsive header and fixed selector, then generates one
rigged round at a time. `enter` selects, and `esc` exits.

Run one deterministic local fixture app loop:

```sh
scorey --local
```

Use these when you want the operator path instead of the app loop:

```sh
scorey play rock
scorey --local play paper
```

Generate live eval samples:

```sh
scorey sample --count 5
```

This stores rows in `.local/evals.sqlite` and prints each generated round.
Use `scorey --local sample --count 5` only for fixture checks.

Initialise the eval database without generating rows:

```sh
scorey eval-init
```

List recent eval rows:

```sh
scorey eval-list
```

Record binary lens judgments:

```sh
scorey judge 1 pass --note "feels like scorey"
scorey judge-round 1 pass --note "complete round shape"
scorey judge-picks 1 pass --note "uses both selected picks"
scorey judge-brat 1 pass --note "bratty not clever"
```

Run checks:

```sh
make check
```

## Output Contract

Each generated round should keep this shape:

```text
you: [rock|paper|scissors]
me: [rock|paper|scissors]

my [me pick] beats your [user pick] because my [me pick] was/were [winning state] and your [user pick] was/were [worse state].

me: [number], you: [fake score or status]

scorey.
```

## Eval Lenses

Scorey keeps product fit as the top-level verdict and stores three sidecar
lenses:

| Lens | Passes When |
| --- | --- |
| `round` | The output includes `you:`, `me:`, one fake rule, and a score. |
| `picks` | In `Beta Eval 1.0`, Scorey picks the object the user's pick would normally beat, or the same object. |
| `brat` | The ending sounds unfair and childish instead of polished or helpful. |
