# synthetic-participants

**Generate structured synthetic personas for piloting research instruments — discussion guides, screeners, and interview training — before fieldwork begins.**

Part of the [CPR Orbital Series](https://github.com/kgkazakos) — 40 open-source tools for AI-native product research, shipping every Friday.

---

## What this is — and what it is not

**This is a pre-fieldwork instrument testing tool.**

Synthetic profiles are intended for:
- Piloting discussion guides before you recruit real participants
- Stress-testing screener logic and quota structures
- Training interviewers and junior researchers on realistic-feeling personas
- Exploring study designs and question flow in early planning

**They are not a substitute for real participants in actual studies.**

Research findings must come from real people. Using synthetic profiles as stand-ins for real participant data would be a methodological and ethical violation. This tool exists to help you run *better* real studies — not to replace them.

If you are looking for a tool that challenges your research framing using simulated persona debate, see [Synthetic User Council](https://github.com/kgkazakos/synthetic-user-council) — a separate, complementary project.

---

## How it relates to Synthetic User Council

These are two different tools with different jobs:

| | synthetic-participants | [Synthetic User Council](https://github.com/kgkazakos/synthetic-user-council) |
|---|---|---|
| **What it does** | Generates structured behavioral profiles | Runs a multi-agent debate to challenge your research framing |
| **Input** | Configuration (n, age range, literacy, etc.) | A research brief |
| **Output** | Persona profiles with traits, contradictions, narrative | Blind spots, challenged assumptions, sharper interview questions |
| **Use it when** | You need stand-ins to pilot instruments | You need your framing stress-tested before fieldwork |

They are designed to complement each other. `synthetic-participants` produces the behavioral profiles; Synthetic User Council puts those kinds of personas to work interrogating your research design.

---

## Features

- **Fully rule-based core** — no API key needed; runs offline
- **Behavioural contradiction detection** — flags internal tensions (e.g. "analytical decision-maker who adopts tools impulsively") using a library of research-grounded rules
- **Reproducible panels** — seed control for consistent output across runs and teammates
- **Diversity reporting** — age, gender, literacy, and adoption distribution summaries
- **Optional LLM narrative enrichment** — Anthropic, OpenAI, or Gemini backends add 3–4 sentence behavioural narratives when richer profiles are needed
- **JSON output mode** — pipe-friendly for CI and pipeline integration
- **Three commands**: `generate`, `single`, `diversity`

---

## Install

```bash
pip install synthetic-participants
```

With optional LLM backends:

```bash
pip install "synthetic-participants[anthropic]"   # claude-haiku
pip install "synthetic-participants[openai]"      # gpt-4o-mini
pip install "synthetic-participants[gemini]"      # gemini-2.0-flash
pip install "synthetic-participants[all]"         # all three
```

---

## CLI usage

### Generate a panel

```bash
# 5 participants, default settings
synthetic-participants generate

# 10 participants, seeded for reproducibility
synthetic-participants generate --n 10 --seed 42

# Filter by digital literacy
synthetic-participants generate --n 5 --digital-literacy expert

# Fix occupation across all participants
synthetic-participants generate --n 3 --occupation "Product Manager"

# Age range
synthetic-participants generate --n 8 --age-min 25 --age-max 40

# JSON output (CI-friendly)
synthetic-participants generate --n 5 --seed 0 --json-output

# LLM narrative enrichment
synthetic-participants generate --n 3 --llm-backend anthropic
```

### Single participant

```bash
synthetic-participants single P001 --seed 7
synthetic-participants single P001 --json-output
```

### Diversity report

```bash
synthetic-participants diversity --n 20 --seed 42
synthetic-participants diversity --n 20 --json-output
```

---

## Python API

```python
from synthetic_participants import (
    generate_participant,
    generate_panel,
    diversity_report,
    DigitalLiteracy,
)

# Single participant
p = generate_participant(seed=42)
print(p.participant_id)                        # P3A1F2B9
print(p.demographics.occupation)              # "UX Designer"
print(p.behavioral_traits.decision_style)     # DecisionStyle.ANALYTICAL
print(p.contradictions[0].description)        # "Self-describes as data-driven but adopts before evaluating"

# Panel
panel = generate_panel(n=10, seed=0, age_range=(25, 45))

# Diversity report
report = diversity_report(panel)
print(report["participants_with_contradictions"])

# Serialise to dict/JSON
d = p.to_dict()

# LLM enrichment (optional — requires API key env var)
from synthetic_participants.profiler import enrich_with_narrative
p = enrich_with_narrative(p, backend="anthropic")
print(p.narrative)
```

---

## Behavioural contradiction rules

Contradictions make piloting sessions more realistic — your discussion guide needs to hold up against people who don't fit clean archetypes.

| Tension | Description |
|---|---|
| Analytical + Early adopter | Claims data-driven approach but adopts impulsively |
| Expert literacy + Low frustration threshold | Expects invisible UX, no tolerance for friction |
| Low risk tolerance + Early adopter | Averse to risk but consistently first to adopt |
| Task-focused + High platform count | Efficiency-oriented but spread across many platforms |
| Spontaneous + Low risk tolerance | Impulsive decisions, self-describes as risk-averse |
| Laggard + Expert literacy | High skill, deliberate avoidance of new tools |
| Socially-driven + High frustration tolerance | Social motivation, unusually patient with failures |
| Deliberate + High hours online | Careful decision-maker, above-average screen time |

Each participant carries 0–2 contradictions.

---

## Profile dimensions

| Dimension | Fields |
|---|---|
| **Demographics** | age, gender, location, occupation, education, income bracket |
| **Tech profile** | primary device, platforms, digital literacy, apps/day, hours online |
| **Behavioural traits** | decision style, risk tolerance, goal orientation, frustration threshold, adoption pattern |
| **Research context** | prior research experience, availability, preferred method |
| **Derived** | contradictions, narrative (LLM), tags |

---

## JSON output

All commands support `--json-output`. Enums serialise as strings. `narrative` is `null` unless `--llm-backend` is supplied.

```json
{
  "participant_id": "P3A1F2B9",
  "demographics": { "age": 34, "gender": "Woman", "occupation": "Product Manager" },
  "tech_profile": { "digital_literacy": "advanced", "primary_device": "MacBook" },
  "behavioral_traits": { "decision_style": "analytical", "adoption_pattern": "early adopter" },
  "research_context": { "preferred_method": "interview", "prior_research_experience": true },
  "contradictions": [
    {
      "trait_a": "decision_style:analytical",
      "trait_b": "adoption_pattern:early_adopter",
      "description": "Self-describes as data-driven but adopts new tools before completing any evaluation"
    }
  ],
  "narrative": null,
  "tags": ["analytical", "advanced", "early adopter", "task-focused"]
}
```

---

## LLM enrichment

| Backend | Default model | Env var |
|---|---|---|
| `anthropic` | `claude-haiku-20240307` | `ANTHROPIC_API_KEY` |
| `openai` | `gpt-4o-mini` | `OPENAI_API_KEY` |
| `gemini` | `gemini-2.0-flash` | `GOOGLE_API_KEY` |

The rule-based core is complete without LLM enrichment.

---

## Part of the CPR Ecosystem

`synthetic-participants` is **Tool 9** in the CPR Orbital Series.

| Tool | What it does |
|---|---|
| [Synthetic User Council](https://github.com/kgkazakos/synthetic-user-council) | Multi-agent debate that challenges your research framing before fieldwork *(core CPR project)* |
| [transcript-cleaner](https://github.com/kgkazakos/transcript-cleaner) | Fix diarization errors and speaker gaps in raw transcripts |
| [uxr-prompt-pack](https://github.com/kgkazakos/uxr-prompt-pack) | Versioned LLM prompt library with built-in evals |
| [qual-sniffer](https://github.com/kgkazakos/qual-sniffer) | Detect methodological weaknesses in discussion guides |
| [survey-cleaner](https://github.com/kgkazakos/survey-cleaner) | Remove speeders and straight-liners from survey exports |
| [insight-differ](https://github.com/kgkazakos/insight-differ) | Compare two research reports for contradictions and gaps |
| [research-rubric](https://github.com/kgkazakos/research-rubric) | Evaluate qualitative research quality across 8 dimensions |

---

## Development

```bash
git clone https://github.com/kgkazakos/synthetic-participants
cd synthetic-participants
pip install -e ".[dev]" --no-build-isolation
pytest tests/ -v
ruff check synthetic_participants/
```

---

## License

MIT — Kostas Kazakos, 2026
