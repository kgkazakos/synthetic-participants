"""
Rule-based synthetic participant generator.

No API keys required. Participants are generated from structured pools
with behavioural contradiction detection to add psychological realism.
"""

from __future__ import annotations

import random
from typing import List, Optional

from .models import (
    AdoptionPattern,
    BehavioralContradiction,
    BehavioralTraits,
    DecisionStyle,
    Demographics,
    DigitalLiteracy,
    FrustrationThreshold,
    GoalOrientation,
    PreferredMethod,
    ResearchContext,
    RiskTolerance,
    SyntheticParticipant,
    TechProfile,
)

# ── Data pools ────────────────────────────────────────────────────────────────

OCCUPATIONS = [
    "Software Engineer",
    "Product Manager",
    "UX Designer",
    "Marketing Manager",
    "Teacher",
    "Registered Nurse",
    "Accountant",
    "Freelance Consultant",
    "Retail Store Manager",
    "University Student",
    "Operations Lead",
    "Data Analyst",
    "Small Business Owner",
    "HR Business Partner",
    "Content Creator",
    "Financial Advisor",
    "Logistics Coordinator",
    "Graphic Designer",
    "Sales Representative",
    "Research Scientist",
]

LOCATIONS = [
    "San Francisco, CA",
    "New York, NY",
    "Austin, TX",
    "Chicago, IL",
    "Seattle, WA",
    "London, UK",
    "Berlin, Germany",
    "Sydney, Australia",
    "Toronto, Canada",
    "Amsterdam, Netherlands",
    "Singapore",
    "São Paulo, Brazil",
    "Remote (US-based)",
    "Remote (EU-based)",
    "Mumbai, India",
]

EDUCATION_LEVELS = [
    "High school diploma",
    "Some college, no degree",
    "Associate's degree",
    "Bachelor's degree",
    "Master's degree",
    "PhD or doctorate",
    "Professional certification (trade/technical)",
    "MBA",
]

INCOME_BRACKETS = [
    "Under $30k",
    "$30k–$50k",
    "$50k–$75k",
    "$75k–$100k",
    "$100k–$150k",
    "$150k+",
]

GENDERS = ["Woman", "Man", "Non-binary", "Prefer not to say"]

PRIMARY_DEVICES = [
    "iPhone",
    "Android smartphone",
    "Windows laptop",
    "MacBook",
    "iPad",
    "Android tablet",
    "Desktop PC",
    "Chromebook",
]

PLATFORMS = [
    "Instagram",
    "LinkedIn",
    "Twitter/X",
    "TikTok",
    "Facebook",
    "Reddit",
    "YouTube",
    "Slack",
    "Discord",
    "WhatsApp",
    "Telegram",
    "Pinterest",
    "Snapchat",
    "Mastodon",
]

AVAILABILITY_OPTIONS = [
    "Weekday mornings",
    "Weekday afternoons",
    "Weekday evenings",
    "Weekend mornings",
    "Weekend afternoons",
    "Flexible / any time",
]

# ── Contradiction rules ───────────────────────────────────────────────────────

_CONTRADICTION_RULES = [
    (
        lambda t, b: (
            b.decision_style == DecisionStyle.ANALYTICAL
            and b.adoption_pattern == AdoptionPattern.EARLY_ADOPTER
        ),
        "decision_style:analytical",
        "adoption_pattern:early_adopter",
        "Self-describes as data-driven but adopts new tools before completing any evaluation",
    ),
    (
        lambda t, b: (
            t.digital_literacy == DigitalLiteracy.EXPERT
            and b.frustration_threshold == FrustrationThreshold.LOW
        ),
        "digital_literacy:expert",
        "frustration_threshold:low",
        "High technical fluency but zero tolerance for friction — expects invisible UX",
    ),
    (
        lambda t, b: (
            b.risk_tolerance == RiskTolerance.LOW
            and b.adoption_pattern == AdoptionPattern.EARLY_ADOPTER
        ),
        "risk_tolerance:low",
        "adoption_pattern:early_adopter",
        "Self-identifies as risk-averse yet consistently in the first wave of new technology",
    ),
    (
        lambda t, b: (
            b.goal_orientation == GoalOrientation.TASK_FOCUSED
            and len(t.platforms) >= 5
        ),
        "goal_orientation:task-focused",
        "platforms:high_count",
        "Primarily task-focused but maintains active presence across many social platforms",
    ),
    (
        lambda t, b: (
            b.decision_style == DecisionStyle.SPONTANEOUS
            and b.risk_tolerance == RiskTolerance.LOW
        ),
        "decision_style:spontaneous",
        "risk_tolerance:low",
        "Makes impulsive decisions but expresses strong aversion to uncertainty when asked",
    ),
    (
        lambda t, b: (
            b.adoption_pattern == AdoptionPattern.LAGGARD
            and t.digital_literacy in (DigitalLiteracy.ADVANCED, DigitalLiteracy.EXPERT)
        ),
        "adoption_pattern:laggard",
        "digital_literacy:advanced+",
        "High digital fluency but deliberately avoids new tools until they are fully established",
    ),
    (
        lambda t, b: (
            b.goal_orientation == GoalOrientation.SOCIALLY_DRIVEN
            and b.frustration_threshold == FrustrationThreshold.HIGH
        ),
        "goal_orientation:socially-driven",
        "frustration_threshold:high",
        "Motivated by social connection but unusually patient with product failures",
    ),
    (
        lambda t, b: (
            b.decision_style == DecisionStyle.DELIBERATE
            and t.hours_online >= 6.0
        ),
        "decision_style:deliberate",
        "hours_online:high",
        "Careful, methodical decision-maker who nonetheless spends an above-average amount of time online",
    ),
]


def _detect_contradictions(
    tech: TechProfile,
    traits: BehavioralTraits,
    rng: random.Random,
) -> List[BehavioralContradiction]:
    """Apply contradiction rules and return 0–2 that fire for this profile."""
    fired = [
        BehavioralContradiction(trait_a=ta, trait_b=tb, description=desc)
        for rule, ta, tb, desc in _CONTRADICTION_RULES
        if rule(tech, traits)
    ]
    # cap at 2 so profiles stay readable
    if len(fired) > 2:
        fired = rng.sample(fired, 2)
    return fired


# ── Core generators ───────────────────────────────────────────────────────────

def generate_participant(
    age_range: tuple[int, int] = (18, 65),
    occupation: Optional[str] = None,
    digital_literacy: Optional[DigitalLiteracy] = None,
    seed: Optional[int] = None,
    participant_id: Optional[str] = None,
) -> SyntheticParticipant:
    """
    Generate a single synthetic participant.

    Parameters
    ----------
    age_range:
        (min, max) inclusive age bounds.
    occupation:
        Fix the participant's occupation. Random if omitted.
    digital_literacy:
        Fix digital literacy level. Random if omitted.
    seed:
        Integer seed for reproducibility.
    participant_id:
        Custom participant ID. Auto-generated if omitted.
    """
    rng = random.Random(seed)

    pid = participant_id or "P" + "".join(
        rng.choices("0123456789ABCDEF", k=8)
    )

    tech = TechProfile(
        primary_device=rng.choice(PRIMARY_DEVICES),
        platforms=rng.sample(PLATFORMS, rng.randint(2, 6)),
        digital_literacy=digital_literacy or rng.choice(list(DigitalLiteracy)),
        apps_per_day=rng.randint(3, 22),
        hours_online=round(rng.uniform(1.0, 9.0), 1),
    )

    traits = BehavioralTraits(
        decision_style=rng.choice(list(DecisionStyle)),
        risk_tolerance=rng.choice(list(RiskTolerance)),
        goal_orientation=rng.choice(list(GoalOrientation)),
        frustration_threshold=rng.choice(list(FrustrationThreshold)),
        adoption_pattern=rng.choice(list(AdoptionPattern)),
    )

    demographics = Demographics(
        age=rng.randint(*age_range),
        gender=rng.choice(GENDERS),
        location=rng.choice(LOCATIONS),
        occupation=occupation or rng.choice(OCCUPATIONS),
        education=rng.choice(EDUCATION_LEVELS),
        income_bracket=rng.choice(INCOME_BRACKETS),
    )

    context = ResearchContext(
        prior_research_experience=rng.choice([True, False]),
        screener_answers={},
        availability=rng.choice(AVAILABILITY_OPTIONS),
        preferred_method=rng.choice(list(PreferredMethod)),
    )

    contradictions = _detect_contradictions(tech, traits, rng)

    tags = [
        traits.decision_style.value,
        tech.digital_literacy.value,
        traits.adoption_pattern.value,
        traits.goal_orientation.value,
    ]

    return SyntheticParticipant(
        participant_id=pid,
        demographics=demographics,
        tech_profile=tech,
        behavioral_traits=traits,
        research_context=context,
        contradictions=contradictions,
        narrative=None,
        tags=tags,
    )


def generate_panel(
    n: int = 10,
    age_range: tuple[int, int] = (18, 65),
    occupation: Optional[str] = None,
    digital_literacy: Optional[DigitalLiteracy] = None,
    seed: Optional[int] = None,
) -> List[SyntheticParticipant]:
    """
    Generate a panel of n synthetic participants.

    When ``seed`` is provided the panel is fully reproducible — each
    participant gets a deterministic sub-seed derived from the root.
    """
    rng = random.Random(seed)
    participants = []
    for i in range(n):
        sub_seed = rng.randint(0, 2**31) if seed is not None else None
        p = generate_participant(
            age_range=age_range,
            occupation=occupation,
            digital_literacy=digital_literacy,
            seed=sub_seed,
        )
        participants.append(p)
    return participants


def diversity_report(panel: List[SyntheticParticipant]) -> dict:
    """
    Compute simple diversity statistics across a panel.

    Useful for confirming a panel isn't accidentally homogeneous.
    """
    if not panel:
        return {}

    ages = [p.demographics.age for p in panel]
    genders = [p.demographics.gender for p in panel]
    literacies = [p.tech_profile.digital_literacy.value for p in panel]
    adoptions = [p.behavioral_traits.adoption_pattern.value for p in panel]

    def _counts(lst: list) -> dict:
        out: dict = {}
        for v in lst:
            out[v] = out.get(v, 0) + 1
        return dict(sorted(out.items()))

    return {
        "n": len(panel),
        "age": {
            "min": min(ages),
            "max": max(ages),
            "mean": round(sum(ages) / len(ages), 1),
        },
        "gender_distribution": _counts(genders),
        "digital_literacy_distribution": _counts(literacies),
        "adoption_pattern_distribution": _counts(adoptions),
        "participants_with_contradictions": sum(
            1 for p in panel if p.contradictions
        ),
    }
