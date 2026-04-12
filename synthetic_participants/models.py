"""Core dataclasses for synthetic-participants."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class DigitalLiteracy(str, Enum):
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class DecisionStyle(str, Enum):
    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"
    DELIBERATE = "deliberate"
    SPONTANEOUS = "spontaneous"


class RiskTolerance(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class GoalOrientation(str, Enum):
    TASK_FOCUSED = "task-focused"
    EXPLORATORY = "exploratory"
    SOCIALLY_DRIVEN = "socially-driven"


class FrustrationThreshold(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AdoptionPattern(str, Enum):
    EARLY_ADOPTER = "early adopter"
    MAINSTREAM = "mainstream"
    LATE_MAJORITY = "late majority"
    LAGGARD = "laggard"


class PreferredMethod(str, Enum):
    INTERVIEW = "interview"
    USABILITY_TEST = "usability test"
    DIARY_STUDY = "diary study"
    SURVEY = "survey"


@dataclass
class Demographics:
    age: int
    gender: str
    location: str
    occupation: str
    education: str
    income_bracket: str


@dataclass
class TechProfile:
    primary_device: str
    platforms: List[str]
    digital_literacy: DigitalLiteracy
    apps_per_day: int
    hours_online: float


@dataclass
class BehavioralTraits:
    decision_style: DecisionStyle
    risk_tolerance: RiskTolerance
    goal_orientation: GoalOrientation
    frustration_threshold: FrustrationThreshold
    adoption_pattern: AdoptionPattern


@dataclass
class ResearchContext:
    prior_research_experience: bool
    screener_answers: Dict[str, str]
    availability: str
    preferred_method: PreferredMethod


@dataclass
class BehavioralContradiction:
    trait_a: str
    trait_b: str
    description: str


@dataclass
class SyntheticParticipant:
    participant_id: str
    demographics: Demographics
    tech_profile: TechProfile
    behavioral_traits: BehavioralTraits
    research_context: ResearchContext
    contradictions: List[BehavioralContradiction] = field(default_factory=list)
    narrative: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "participant_id": self.participant_id,
            "demographics": {
                "age": self.demographics.age,
                "gender": self.demographics.gender,
                "location": self.demographics.location,
                "occupation": self.demographics.occupation,
                "education": self.demographics.education,
                "income_bracket": self.demographics.income_bracket,
            },
            "tech_profile": {
                "primary_device": self.tech_profile.primary_device,
                "platforms": self.tech_profile.platforms,
                "digital_literacy": self.tech_profile.digital_literacy.value,
                "apps_per_day": self.tech_profile.apps_per_day,
                "hours_online": self.tech_profile.hours_online,
            },
            "behavioral_traits": {
                "decision_style": self.behavioral_traits.decision_style.value,
                "risk_tolerance": self.behavioral_traits.risk_tolerance.value,
                "goal_orientation": self.behavioral_traits.goal_orientation.value,
                "frustration_threshold": self.behavioral_traits.frustration_threshold.value,
                "adoption_pattern": self.behavioral_traits.adoption_pattern.value,
            },
            "research_context": {
                "prior_research_experience": self.research_context.prior_research_experience,
                "screener_answers": self.research_context.screener_answers,
                "availability": self.research_context.availability,
                "preferred_method": self.research_context.preferred_method.value,
            },
            "contradictions": [
                {
                    "trait_a": c.trait_a,
                    "trait_b": c.trait_b,
                    "description": c.description,
                }
                for c in self.contradictions
            ],
            "narrative": self.narrative,
            "tags": self.tags,
        }
