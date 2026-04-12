"""
Basic usage examples for synthetic-participants.

Run this file directly to see the library in action without any API keys.
"""

import json
from synthetic_participants import (
    generate_participant,
    generate_panel,
    diversity_report,
    DigitalLiteracy,
)


def example_single_participant():
    print("=" * 60)
    print("Example 1: Single participant (seed=42 for reproducibility)")
    print("=" * 60)
    p = generate_participant(seed=42)
    print(f"ID:            {p.participant_id}")
    print(f"Age/Gender:    {p.demographics.age}yo {p.demographics.gender}")
    print(f"Occupation:    {p.demographics.occupation}")
    print(f"Location:      {p.demographics.location}")
    print(f"Literacy:      {p.tech_profile.digital_literacy.value}")
    print(f"Decision:      {p.behavioral_traits.decision_style.value}")
    print(f"Adoption:      {p.behavioral_traits.adoption_pattern.value}")
    if p.contradictions:
        print(f"Contradictions:")
        for c in p.contradictions:
            print(f"  ⚡ {c.description}")
    print()


def example_panel():
    print("=" * 60)
    print("Example 2: Panel of 5 participants (seed=0)")
    print("=" * 60)
    panel = generate_panel(n=5, seed=0)
    for p in panel:
        tensions = len(p.contradictions)
        print(
            f"  {p.participant_id}  {p.demographics.age}yo  "
            f"{p.demographics.occupation:<30}  "
            f"literacy={p.tech_profile.digital_literacy.value:<14}  "
            f"tensions={tensions}"
        )
    print()


def example_diversity():
    print("=" * 60)
    print("Example 3: Diversity report for 20 participants")
    print("=" * 60)
    panel = generate_panel(n=20, seed=1)
    report = diversity_report(panel)
    print(json.dumps(report, indent=2))
    print()


def example_fixed_literacy():
    print("=" * 60)
    print("Example 4: Panel filtered to expert digital literacy")
    print("=" * 60)
    panel = generate_panel(n=3, digital_literacy=DigitalLiteracy.EXPERT, seed=7)
    for p in panel:
        print(f"  {p.participant_id}  {p.tech_profile.digital_literacy.value}  {p.demographics.occupation}")
    print()


def example_serialisation():
    print("=" * 60)
    print("Example 5: JSON serialisation")
    print("=" * 60)
    p = generate_participant(seed=123)
    d = p.to_dict()
    print(json.dumps(d, indent=2)[:800])
    print("  ... (truncated)")
    print()


if __name__ == "__main__":
    example_single_participant()
    example_panel()
    example_diversity()
    example_fixed_literacy()
    example_serialisation()
