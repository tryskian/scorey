<!-- @format -->

# Research Template Folder

Local peanut draft for splitting the `scorey` research-doc standard into
reusable category templates.

## Kernel

| Rule | Choice |
| --- | --- |
| Target folder | `docs/research/` |
| Entry file | `README.md` |
| Legend file | `000_LEGEND.md` |
| Filename shape | `NNN_CODE.md` or `NNN_CODE-QUALIFIER.md` |
| Boundary code rule | `B` for beta boundaries, `PB` for staged pre-beta boundaries |
| Dates | inside docs, not filenames |
| Default style | concise and visual-forward |
| First content surface | table or diagram |

## Template Files

| Template | Use For |
| --- | --- |
| [legend.md](legend.md) | `000_LEGEND.md` |
| [boundary.md](boundary.md) | beta or method boundary docs |
| [lane.md](lane.md) | current evidence lane docs |
| [case.md](case.md) | representative artefact or case docs |
| [validation.md](validation.md) | run, soak, or gate proof docs |
| [hypothesis.md](hypothesis.md) | staged hypothesis docs |
| [backlog.md](backlog.md) | source pool and candidate family docs |

## Code Ranges

| Range | Role |
| ---: | --- |
| `000` | index and legend |
| `010-099` | closed or active beta boundaries |
| `100-199` | route and tone lane docs |
| `200-299` | bounded lens and family lane docs |
| `300-399` | operator gate and validation lane docs |
| `400-499` | staged pre-beta boundaries, hypotheses, and backlog |

## Boundary Filename Shape

Use boundary files like this in `scorey`:

- `NNN_B-NAME.md`
  - active or closed beta boundary
- `NNN_PB-NAME.md`
  - staged pre-beta boundary

Examples:

- `040_B-ABSTRACT_TONE_MEASUREMENT.md`
- `070_B-BROADER_PROSE_JUDGEMENT.md`
- `410_PB-MENACE_JUDGEMENT.md`

## Shared Metadata

Every category template starts with this table shape.

| Field | Value |
| --- | --- |
| Code | short lane code |
| Category | `legend`, `boundary`, `lane`, `case`, `validation`, `hypothesis`, or `backlog` |
| Status | current state |
| Last evidence | `YYYY-MM-DD` |
| Owns | one sentence naming the doc's job |

## Style Rules

- Lead with a table or diagram.
- Use prose only for interpretation.
- Keep inventories in tables.
- Use one or two bullets per prose section.
- Prefer one compact Mermaid diagram when a contrast or eval flow is the point.
