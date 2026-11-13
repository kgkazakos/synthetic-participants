"""
Optional LLM enrichment for synthetic participants.

No API keys are required for core functionality. This module is only
invoked when the --llm-backend flag is supplied via the CLI.

Supported backends: anthropic (claude-haiku), openai (gpt-4o-mini), gemini (gemini-3.6-flash)
"""

from __future__ import annotations

import json
from typing import Optional

from .models import SyntheticParticipant

# ── Prompt template ───────────────────────────────────────────────────────────

_NARRATIVE_PROMPT = """\
You are a senior UX researcher writing a participant profile summary.

Given the structured profile below, write a 3–4 sentence behavioural narrative \
in third person. Capture:
- How this person interacts with digital products day-to-day
- One concrete, specific habit or pattern (not a generic statement)
- Any notable tension or contradiction in their behaviour if one is listed
- What would delight or frustrate them as a user

Avoid generic language. Sound like a real person described by a skilled researcher.
Do not start with the participant's ID.

Profile:
{profile_json}
"""


def _build_prompt(participant: SyntheticParticipant) -> str:
    profile = {
        "age": participant.demographics.age,
        "gender": participant.demographics.gender,
        "occupation": participant.demographics.occupation,
        "location": participant.demographics.location,
        "education": participant.demographics.education,
        "income_bracket": participant.demographics.income_bracket,
        "primary_device": participant.tech_profile.primary_device,
        "platforms": participant.tech_profile.platforms,
        "digital_literacy": participant.tech_profile.digital_literacy.value,
        "hours_online_per_day": participant.tech_profile.hours_online,
        "apps_per_day": participant.tech_profile.apps_per_day,
        "decision_style": participant.behavioral_traits.decision_style.value,
        "risk_tolerance": participant.behavioral_traits.risk_tolerance.value,
        "goal_orientation": participant.behavioral_traits.goal_orientation.value,
        "frustration_threshold": participant.behavioral_traits.frustration_threshold.value,
        "adoption_pattern": participant.behavioral_traits.adoption_pattern.value,
        "preferred_method": participant.research_context.preferred_method.value,
        "prior_research_experience": participant.research_context.prior_research_experience,
        "behavioral_contradictions": [
            c.description for c in participant.contradictions
        ],
    }
    return _NARRATIVE_PROMPT.format(profile_json=json.dumps(profile, indent=2))


# ── Backend callers ───────────────────────────────────────────────────────────

def _call_anthropic(prompt: str, model: str) -> str:
    import anthropic  # type: ignore

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=model,
        max_tokens=350,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def _call_openai(prompt: str, model: str) -> str:
    from openai import OpenAI  # type: ignore

    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=350,
    )
    return resp.choices[0].message.content.strip()


def _call_gemini(prompt: str, model: str) -> str:
    import google.generativeai as genai  # type: ignore

    m = genai.GenerativeModel(model)
    resp = m.generate_content(prompt)
    return resp.text.strip()


_BACKENDS = {
    "anthropic": (_call_anthropic, "claude-haiku-20240307"),
    "openai": (_call_openai, "gpt-4o-mini"),
    "gemini": (_call_gemini, "gemini-3.6-flash"),
}

# ── Public API ────────────────────────────────────────────────────────────────

def enrich_with_narrative(
    participant: SyntheticParticipant,
    backend: str = "anthropic",
    model: Optional[str] = None,
) -> SyntheticParticipant:
    """
    Enrich a participant with an LLM-generated behavioural narrative.

    Mutates ``participant.narrative`` in place and returns the participant.

    Parameters
    ----------
    participant:
        The participant to enrich.
    backend:
        One of 'anthropic', 'openai', 'gemini'.
    model:
        Override the default model for the chosen backend.
    """
    if backend not in _BACKENDS:
        raise ValueError(
            f"Unknown backend '{backend}'. Choose from: {', '.join(_BACKENDS)}"
        )

    caller, default_model = _BACKENDS[backend]
    prompt = _build_prompt(participant)
    participant.narrative = caller(prompt, model or default_model)
    return participant


def enrich_panel(
    participants: list[SyntheticParticipant],
    backend: str = "anthropic",
    model: Optional[str] = None,
) -> tuple[list[SyntheticParticipant], list[str]]:
    """
    Enrich a list of participants with narratives.

    Returns (enriched_participants, errors) where errors is a list of
    participant IDs that failed enrichment.
    """
    errors: list[str] = []
    for p in participants:
        try:
            enrich_with_narrative(p, backend=backend, model=model)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{p.participant_id}: {exc}")
    return participants, errors
