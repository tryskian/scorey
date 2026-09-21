# Pipeline

This is the canonical day-zero public shape for how Scorey should generate one
rigged rock, paper, scissors round.

The runtime now exists. This page records the contract shape it should
preserve as the project evolves.

## Canonical Diagram

```mermaid
flowchart TD
  A["User pick"]
  B["Scorey pick"]
  C["Matchup route"]
  D["Scorey winning state"]
  E["User worse state"]
  F["Scoreboard claim"]
  H["Compose response"]
  I["Final round"]

  A --> B
  A --> C
  B --> C
  C --> D
  C --> E
  D --> H
  E --> H
  F --> H
  H --> I
```

## Reading Note

Scorey is not a general joke generator. The route starts with the user's actual
pick and Scorey's actual pick, then invents a reason that preserves both sides
of the round.

Different-pick rounds use cross-object fake rules.

Same-pick rounds use comparison rules rather than tie handling.

Every round ends with Scorey's unfair tone and a scoreboard claim that treats
Scorey's win as already official.

## Allowed Routes

| User Pick | Allowed Scorey Picks | Route Families |
| --- | --- | --- |
| `rock` | `scissors`, `rock` | cross-object, same-pick |
| `paper` | `rock`, `paper` | cross-object, same-pick |
| `scissors` | `paper`, `scissors` | cross-object, same-pick |

Different-pick rounds use cross-object fake rules.

Same-pick rounds use version-loophole comparison rules. They are not ties.

## Ownership Boundary

| Field | Owner | Job |
| --- | --- | --- |
| `user_pick` | runtime | preserve the selected pick |
| `scorey_pick` | runtime | enforce valid routing |
| `route_family` | runtime | select the round rule family |
| `winning_state` | model | explain why Scorey's version wins |
| `worse_state` | model | explain why the user's version loses |
| `scoreboard_claim` | model | provide the small unfair score-side claim |
| final round composition | runtime | output labels, prose shape, and closing tag |

## Final Round Shape

```text
you: [rock|paper|scissors]
me: [rock|paper|scissors]

my [scorey pick] beats your [user pick] because my [scorey pick] was/were [winning state] and your [user pick] was/were [worse state].

me: [scorey score], you: [scoreboard claim]

scorey.
```

The score line must present Scorey as ahead after the round.

## Opt-in Source-Linked Retrieval

This path is implemented but opt-in, and it is separate from the default
runtime and the current Beta 1 local run. It keeps runtime-selected picks and
route authoritative, retrieves from a frozen local SQLite snapshot built from
four exact source-linked pipeline principles, and passes bounded context into
the existing three-field generation path. The snapshot defaults to
`text-embedding-3-small` and is pinned by `SCOREY_MEMORY_INDEX` while
`SCOREY_MEMORY_ENABLED` is enabled. Build validates each excerpt against its
source document and stores the complete source-document hashes.

```mermaid
flowchart LR
  P["Runtime-selected picks + route"]
  V["Frozen local SQLite<br/>source-linked snapshot"]
  R["Retrieve relevant<br/>Scorey context"]
  F["Generate the existing<br/>three round fields"]
  C["Runtime composition"]
  O["Live eval output"]
  Q["Selected sources + index<br/>provenance receipt"]

  P --> R
  V --> R
  R -->|"bounded prompt context"| F
  F --> C
  C --> O
  R -.-> Q
  Q -.-> O
```

The provenance receipt sits beside the live eval output as metadata. It is not a
new research gate, verdict, or replacement for the existing eval stack. Retrieval
uses the route filter, `top_k=2`, and `max_chars=1200`; the per-round path does
not make an embedding request. A source change requires a new build and pin.
Activation is per named local condition. Behavioral efficacy is measured under
the existing gates, and this path does not advance Beta 1 or any later beta.

## Eval Shape Diagram

```mermaid
flowchart TD
  I["Final round"]
  J["Round contract"]
  K["Pick relevance"]
  L["Tone fit"]
  M["Product fit"]

  I --> J
  J --> K
  J --> L
  K --> M
  L --> M
```

## Post-Fail Gate Stack

```mermaid
flowchart LR
  A["Judged round"] --> B{"PASS / FAIL"}
  B -->|"PASS"| C["Keep confidence in active lane"]
  B -->|"FAIL"| D["Failure evidence"]
  D --> E{"RETAIN / EVICT"}
  E -->|"RETAIN"| F["Keep row in active lane"]
  F --> G["Accumulate more judged signal"]
  G --> A
  E -->|"EVICT"| H["Upstream route or lane correction"]
  H --> I["Rerun corrected lane"]
  I --> A
```

## Eval Shape Reading Note

The first active eval kernel should stay narrow:

- does the round preserve the chosen picks?
- does the route stay valid?
- does the output keep a legible round shape?
- current `Research Beta 1.0` only judges the pick pair in `scorey_pick, user_pick` order
- `pass`:
  - `paper, scissors`
  - `rock, paper`
  - `scissors, rock`
  - `paper, paper`
  - `rock, rock`
  - `scissors, scissors`
- `fail`:
  - every other pick pair

Broader taste judgements should only harden after the round contract is stable.

That gate stays binary first:

- `PASS / FAIL`
- if `FAIL`, then `RETAIN / EVICT`
- rerun
- `PASS / FAIL`
