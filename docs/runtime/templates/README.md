<!-- @format -->

# Research template folder

Reusable templates for the tracked `docs/research/` lane. They describe a
document shape; they are not evidence or an active method by themselves.

The charter's [document naming standard](../../governance/CHARTER.md#document-naming)
covers the other document types. Research-specific rules follow below.

## Kernel

| Rule | Choice |
| --- | --- |
| Entry | `docs/research/README.md` |
| Legend | `000_LEGEND.md` |
| Filename | `NNN_CODE.md` or `NNN_CODE-QUALIFIER.md` |
| Boundary filenames | `NNN_B-NAME.md` for beta boundaries; `NNN_PB-NAME.md` for staged pre-beta boundaries |
| Dates | Inside documents, not filenames |
| Style | Concise, visual-forward, table or diagram first |

## Templates

| Template | Use for |
| --- | --- |
| [legend.md](legend.md) | `000_LEGEND.md` |
| [boundary.md](boundary.md) | Beta or method boundaries |
| [lane.md](lane.md) | Current evidence lanes |
| [case.md](case.md) | Representative artefacts or cases |
| [validation.md](validation.md) | Run, soak or gate proof |
| [hypothesis.md](hypothesis.md) | Staged hypotheses |
| [backlog.md](backlog.md) | Source pools and candidate families |

## Code ranges

| Range | Role |
| ---: | --- |
| `000` | Index and legend |
| `010-099` | Closed or active beta boundaries |
| `100-199` | Route and tone lanes |
| `200-299` | Bounded lens and family lanes |
| `300-399` | Operator gates and validation |
| `400-499` | Staged pre-beta boundaries, hypotheses and backlog |

Examples: `040_B-ABSTRACT_TONE_MEASUREMENT.md` and
`410_PB-POSITIVE_RUNTIME_INSTRUCTION_CONTRACT.md`.

## Shared metadata and style

Every template begins with:

| Field | Value |
| --- | --- |
| Code | Short lane code |
| Category | `legend`, `boundary`, `lane`, `case`, `validation`, `hypothesis` or `backlog` |
| Status | Current state |
| Last evidence | `YYYY-MM-DD` |
| Owns | One sentence naming the document's job |

Apply the [charter's concision rule](../../governance/CHARTER.md#document-roles):
use concise, natural language within the selected template, preserving required
structure and evidence. Lead with the useful point, keep inventories in tables,
and use one or two bullets per prose section. A diagram is useful only when it
makes the evidence or relationship clearer.
