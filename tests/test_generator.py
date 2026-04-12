"""Tests for generator.py — participant generation and diversity reporting."""

import pytest

from synthetic_participants.generator import (
    diversity_report,
    generate_panel,
    generate_participant,
)
from synthetic_participants.models import (
    AdoptionPattern,
    DecisionStyle,
    DigitalLiteracy,
    FrustrationThreshold,
    GoalOrientation,
    RiskTolerance,
    SyntheticParticipant,
)


# ── generate_participant ──────────────────────────────────────────────────────

def test_generate_participant_returns_type():
    p = generate_participant()
    assert isinstance(p, SyntheticParticipant)


def test_generate_participant_has_id():
    p = generate_participant()
    assert p.participant_id.startswith("P")
    assert len(p.participant_id) > 1


def test_generate_participant_custom_id():
    p = generate_participant(participant_id="TEST_01")
    assert p.participant_id == "TEST_01"


def test_generate_participant_age_range():
    for _ in range(30):
        p = generate_participant(age_range=(25, 30))
        assert 25 <= p.demographics.age <= 30


def test_generate_participant_age_range_single():
    p = generate_participant(age_range=(40, 40))
    assert p.demographics.age == 40


def test_generate_participant_fixed_occupation():
    p = generate_participant(occupation="Nurse")
    assert p.demographics.occupation == "Nurse"


def test_generate_participant_fixed_digital_literacy():
    p = generate_participant(digital_literacy=DigitalLiteracy.EXPERT)
    assert p.tech_profile.digital_literacy == DigitalLiteracy.EXPERT


def test_generate_participant_seed_reproducible():
    p1 = generate_participant(seed=42)
    p2 = generate_participant(seed=42)
    assert p1.demographics.age == p2.demographics.age
    assert p1.demographics.occupation == p2.demographics.occupation
    assert p1.tech_profile.digital_literacy == p2.tech_profile.digital_literacy
    assert p1.behavioral_traits.decision_style == p2.behavioral_traits.decision_style


def test_generate_participant_different_seeds_differ():
    p1 = generate_participant(seed=1)
    p2 = generate_participant(seed=99)
    # profiles should differ on at least something across 5 fields
    diffs = sum([
        p1.demographics.age != p2.demographics.age,
        p1.demographics.occupation != p2.demographics.occupation,
        p1.tech_profile.digital_literacy != p2.tech_profile.digital_literacy,
        p1.behavioral_traits.decision_style != p2.behavioral_traits.decision_style,
        p1.behavioral_traits.risk_tolerance != p2.behavioral_traits.risk_tolerance,
    ])
    assert diffs >= 1


def test_generate_participant_platforms_range():
    for _ in range(20):
        p = generate_participant()
        assert 2 <= len(p.tech_profile.platforms) <= 6


def test_generate_participant_no_duplicate_platforms():
    for _ in range(20):
        p = generate_participant()
        assert len(p.tech_profile.platforms) == len(set(p.tech_profile.platforms))


def test_generate_participant_hours_online_range():
    for _ in range(20):
        p = generate_participant()
        assert 1.0 <= p.tech_profile.hours_online <= 9.0


def test_generate_participant_apps_per_day_range():
    for _ in range(20):
        p = generate_participant()
        assert 3 <= p.tech_profile.apps_per_day <= 22


def test_generate_participant_traits_are_enums():
    p = generate_participant(seed=7)
    assert isinstance(p.behavioral_traits.decision_style, DecisionStyle)
    assert isinstance(p.behavioral_traits.risk_tolerance, RiskTolerance)
    assert isinstance(p.behavioral_traits.goal_orientation, GoalOrientation)
    assert isinstance(p.behavioral_traits.frustration_threshold, FrustrationThreshold)
    assert isinstance(p.behavioral_traits.adoption_pattern, AdoptionPattern)


def test_generate_participant_has_tags():
    p = generate_participant(seed=5)
    assert isinstance(p.tags, list)
    assert len(p.tags) > 0


def test_generate_participant_contradictions_list():
    p = generate_participant(seed=0)
    assert isinstance(p.contradictions, list)
    assert len(p.contradictions) <= 2


def test_generate_participant_narrative_none_by_default():
    p = generate_participant()
    assert p.narrative is None


def test_generate_participant_research_context_complete():
    p = generate_participant()
    assert isinstance(p.research_context.prior_research_experience, bool)
    assert isinstance(p.research_context.availability, str)
    assert p.research_context.screener_answers == {}


# ── generate_panel ────────────────────────────────────────────────────────────

def test_generate_panel_count():
    panel = generate_panel(n=10)
    assert len(panel) == 10


def test_generate_panel_count_zero():
    panel = generate_panel(n=0)
    assert panel == []


def test_generate_panel_count_one():
    panel = generate_panel(n=1)
    assert len(panel) == 1


def test_generate_panel_returns_list_of_participants():
    panel = generate_panel(n=5)
    assert all(isinstance(p, SyntheticParticipant) for p in panel)


def test_generate_panel_seed_reproducible():
    panel_a = generate_panel(n=5, seed=42)
    panel_b = generate_panel(n=5, seed=42)
    for a, b in zip(panel_a, panel_b):
        assert a.demographics.age == b.demographics.age
        assert a.demographics.occupation == b.demographics.occupation
        assert a.behavioral_traits.decision_style == b.behavioral_traits.decision_style


def test_generate_panel_ids_unique():
    panel = generate_panel(n=20, seed=99)
    ids = [p.participant_id for p in panel]
    assert len(ids) == len(set(ids))


def test_generate_panel_age_range_respected():
    panel = generate_panel(n=30, age_range=(30, 40), seed=1)
    for p in panel:
        assert 30 <= p.demographics.age <= 40


def test_generate_panel_fixed_occupation():
    panel = generate_panel(n=5, occupation="Teacher")
    assert all(p.demographics.occupation == "Teacher" for p in panel)


def test_generate_panel_fixed_digital_literacy():
    panel = generate_panel(n=5, digital_literacy=DigitalLiteracy.NOVICE)
    assert all(p.tech_profile.digital_literacy == DigitalLiteracy.NOVICE for p in panel)


def test_generate_panel_large():
    panel = generate_panel(n=40, seed=0)
    assert len(panel) == 40


# ── Contradiction detection ───────────────────────────────────────────────────

def test_contradiction_analytical_early_adopter():
    """Force the analytical + early adopter contradiction."""
    from synthetic_participants.generator import _detect_contradictions
    from synthetic_participants.models import (
        BehavioralTraits,
        TechProfile,
        DecisionStyle,
        RiskTolerance,
        GoalOrientation,
        FrustrationThreshold,
        AdoptionPattern,
        DigitalLiteracy,
    )
    import random

    tech = TechProfile(
        primary_device="MacBook",
        platforms=["LinkedIn"],
        digital_literacy=DigitalLiteracy.INTERMEDIATE,
        apps_per_day=5,
        hours_online=3.0,
    )
    traits = BehavioralTraits(
        decision_style=DecisionStyle.ANALYTICAL,
        risk_tolerance=RiskTolerance.MEDIUM,
        goal_orientation=GoalOrientation.TASK_FOCUSED,
        frustration_threshold=FrustrationThreshold.MEDIUM,
        adoption_pattern=AdoptionPattern.EARLY_ADOPTER,
    )
    rng = random.Random(0)
    contradictions = _detect_contradictions(tech, traits, rng)
    descriptions = [c.description for c in contradictions]
    assert any("data-driven" in d for d in descriptions)


def test_contradiction_expert_low_frustration():
    """Expert digital literacy + low frustration threshold fires."""
    from synthetic_participants.generator import _detect_contradictions
    from synthetic_participants.models import (
        BehavioralTraits,
        TechProfile,
        DecisionStyle,
        RiskTolerance,
        GoalOrientation,
        FrustrationThreshold,
        AdoptionPattern,
        DigitalLiteracy,
    )
    import random

    tech = TechProfile(
        primary_device="iPhone",
        platforms=["Twitter/X"],
        digital_literacy=DigitalLiteracy.EXPERT,
        apps_per_day=8,
        hours_online=5.0,
    )
    traits = BehavioralTraits(
        decision_style=DecisionStyle.DELIBERATE,
        risk_tolerance=RiskTolerance.HIGH,
        goal_orientation=GoalOrientation.TASK_FOCUSED,
        frustration_threshold=FrustrationThreshold.LOW,
        adoption_pattern=AdoptionPattern.MAINSTREAM,
    )
    rng = random.Random(0)
    contradictions = _detect_contradictions(tech, traits, rng)
    descriptions = [c.description for c in contradictions]
    assert any("fluency" in d or "friction" in d for d in descriptions)


def test_contradiction_cap_at_two():
    """No participant should have more than 2 contradictions."""
    panel = generate_panel(n=50, seed=42)
    for p in panel:
        assert len(p.contradictions) <= 2


# ── diversity_report ──────────────────────────────────────────────────────────

def test_diversity_report_empty():
    assert diversity_report([]) == {}


def test_diversity_report_keys():
    panel = generate_panel(n=10, seed=0)
    report = diversity_report(panel)
    assert "n" in report
    assert "age" in report
    assert "gender_distribution" in report
    assert "digital_literacy_distribution" in report
    assert "adoption_pattern_distribution" in report
    assert "participants_with_contradictions" in report


def test_diversity_report_n():
    panel = generate_panel(n=15, seed=0)
    report = diversity_report(panel)
    assert report["n"] == 15


def test_diversity_report_age_stats():
    panel = generate_panel(n=20, age_range=(20, 30), seed=0)
    report = diversity_report(panel)
    assert report["age"]["min"] >= 20
    assert report["age"]["max"] <= 30
    assert 20 <= report["age"]["mean"] <= 30


def test_diversity_report_gender_counts():
    panel = generate_panel(n=20, seed=0)
    report = diversity_report(panel)
    total = sum(report["gender_distribution"].values())
    assert total == 20


def test_diversity_report_literacy_counts():
    panel = generate_panel(n=20, seed=0)
    report = diversity_report(panel)
    total = sum(report["digital_literacy_distribution"].values())
    assert total == 20


def test_diversity_report_contradictions_count():
    panel = generate_panel(n=20, seed=0)
    report = diversity_report(panel)
    count = report["participants_with_contradictions"]
    assert 0 <= count <= 20
