"""Tests for models.py — dataclasses, enums, and serialisation."""

import pytest

from synthetic_participants.models import (
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


# ── Enum completeness ─────────────────────────────────────────────────────────

def test_digital_literacy_values():
    assert set(DigitalLiteracy) == {
        DigitalLiteracy.NOVICE,
        DigitalLiteracy.INTERMEDIATE,
        DigitalLiteracy.ADVANCED,
        DigitalLiteracy.EXPERT,
    }


def test_decision_style_values():
    assert len(list(DecisionStyle)) == 4


def test_adoption_pattern_values():
    assert AdoptionPattern.EARLY_ADOPTER.value == "early adopter"
    assert AdoptionPattern.LAGGARD.value == "laggard"


def test_risk_tolerance_values():
    for v in ("low", "medium", "high"):
        assert RiskTolerance(v) is not None


def test_goal_orientation_values():
    assert GoalOrientation.TASK_FOCUSED.value == "task-focused"
    assert GoalOrientation.SOCIALLY_DRIVEN.value == "socially-driven"


def test_preferred_method_values():
    assert len(list(PreferredMethod)) == 4


# ── Dataclass instantiation ───────────────────────────────────────────────────

@pytest.fixture
def sample_participant():
    return SyntheticParticipant(
        participant_id="P001",
        demographics=Demographics(
            age=32,
            gender="Woman",
            location="London, UK",
            occupation="UX Designer",
            education="Master's degree",
            income_bracket="$75k–$100k",
        ),
        tech_profile=TechProfile(
            primary_device="MacBook",
            platforms=["LinkedIn", "Instagram"],
            digital_literacy=DigitalLiteracy.ADVANCED,
            apps_per_day=10,
            hours_online=5.5,
        ),
        behavioral_traits=BehavioralTraits(
            decision_style=DecisionStyle.ANALYTICAL,
            risk_tolerance=RiskTolerance.MEDIUM,
            goal_orientation=GoalOrientation.TASK_FOCUSED,
            frustration_threshold=FrustrationThreshold.LOW,
            adoption_pattern=AdoptionPattern.EARLY_ADOPTER,
        ),
        research_context=ResearchContext(
            prior_research_experience=True,
            screener_answers={},
            availability="Weekday mornings",
            preferred_method=PreferredMethod.INTERVIEW,
        ),
        contradictions=[
            BehavioralContradiction(
                trait_a="decision_style:analytical",
                trait_b="adoption_pattern:early_adopter",
                description="Self-describes as data-driven but adopts before evaluating",
            )
        ],
        narrative=None,
        tags=["analytical", "advanced", "early adopter"],
    )


def test_participant_instantiation(sample_participant):
    assert sample_participant.participant_id == "P001"
    assert sample_participant.demographics.age == 32
    assert sample_participant.tech_profile.digital_literacy == DigitalLiteracy.ADVANCED
    assert sample_participant.behavioral_traits.decision_style == DecisionStyle.ANALYTICAL


def test_participant_contradictions(sample_participant):
    assert len(sample_participant.contradictions) == 1
    assert "analytical" in sample_participant.contradictions[0].trait_a


def test_participant_tags(sample_participant):
    assert "analytical" in sample_participant.tags
    assert "advanced" in sample_participant.tags


def test_participant_narrative_none(sample_participant):
    assert sample_participant.narrative is None


# ── to_dict ───────────────────────────────────────────────────────────────────

def test_to_dict_structure(sample_participant):
    d = sample_participant.to_dict()
    assert "participant_id" in d
    assert "demographics" in d
    assert "tech_profile" in d
    assert "behavioral_traits" in d
    assert "research_context" in d
    assert "contradictions" in d
    assert "narrative" in d
    assert "tags" in d


def test_to_dict_enum_serialised(sample_participant):
    d = sample_participant.to_dict()
    assert d["tech_profile"]["digital_literacy"] == "advanced"
    assert d["behavioral_traits"]["decision_style"] == "analytical"
    assert d["behavioral_traits"]["risk_tolerance"] == "medium"
    assert d["research_context"]["preferred_method"] == "interview"


def test_to_dict_contradictions_serialised(sample_participant):
    d = sample_participant.to_dict()
    assert len(d["contradictions"]) == 1
    c = d["contradictions"][0]
    assert "trait_a" in c
    assert "trait_b" in c
    assert "description" in c


def test_to_dict_narrative_null(sample_participant):
    d = sample_participant.to_dict()
    assert d["narrative"] is None


def test_to_dict_with_narrative(sample_participant):
    sample_participant.narrative = "A thoughtful UX designer who..."
    d = sample_participant.to_dict()
    assert d["narrative"] == "A thoughtful UX designer who..."


def test_to_dict_demographics_complete(sample_participant):
    d = sample_participant.to_dict()
    dem = d["demographics"]
    assert dem["age"] == 32
    assert dem["gender"] == "Woman"
    assert dem["location"] == "London, UK"
    assert dem["occupation"] == "UX Designer"
    assert dem["education"] == "Master's degree"
    assert dem["income_bracket"] == "$75k–$100k"


def test_to_dict_tech_profile_complete(sample_participant):
    d = sample_participant.to_dict()
    tech = d["tech_profile"]
    assert tech["primary_device"] == "MacBook"
    assert "LinkedIn" in tech["platforms"]
    assert tech["apps_per_day"] == 10
    assert tech["hours_online"] == 5.5


def test_to_dict_research_context(sample_participant):
    d = sample_participant.to_dict()
    rc = d["research_context"]
    assert rc["prior_research_experience"] is True
    assert rc["availability"] == "Weekday mornings"
    assert rc["screener_answers"] == {}
