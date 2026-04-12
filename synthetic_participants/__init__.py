"""synthetic-participants — richly profiled synthetic UX research participants."""

from .generator import diversity_report, generate_panel, generate_participant
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

__version__ = "0.1.0"

__all__ = [
    "generate_panel",
    "generate_participant",
    "diversity_report",
    "SyntheticParticipant",
    "Demographics",
    "TechProfile",
    "BehavioralTraits",
    "BehavioralContradiction",
    "ResearchContext",
    "DigitalLiteracy",
    "DecisionStyle",
    "RiskTolerance",
    "GoalOrientation",
    "FrustrationThreshold",
    "AdoptionPattern",
    "PreferredMethod",
]
