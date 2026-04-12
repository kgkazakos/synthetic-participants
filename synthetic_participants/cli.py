"""
CLI entry point for synthetic-participants.

Commands
--------
generate   Generate a panel of N synthetic participants
single     Generate and display a single participant by ID
diversity  Print a diversity summary for a generated panel
"""

from __future__ import annotations

import json
import sys
from typing import Optional

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .generator import (
    DigitalLiteracy,
    diversity_report,
    generate_panel,
    generate_participant,
)
from .models import SyntheticParticipant

console = Console()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _participant_to_json_dict(p: SyntheticParticipant) -> dict:
    return p.to_dict()


def _print_participant(p: SyntheticParticipant, console: Console = console) -> None:
    d = p.demographics
    t = p.tech_profile
    b = p.behavioral_traits
    r = p.research_context

    title = (
        f"[bold]{p.participant_id}[/bold]  "
        f"[dim]·[/dim]  {d.age}yo {d.gender}  "
        f"[dim]·[/dim]  {d.occupation}  "
        f"[dim]·[/dim]  {d.location}"
    )

    lines = [
        f"[dim]Education:[/dim]   {d.education}",
        f"[dim]Income:[/dim]      {d.income_bracket}",
        "",
        f"[dim]Device:[/dim]      {t.primary_device}    "
        f"[dim]Literacy:[/dim] {t.digital_literacy.value.title()}",
        f"[dim]Platforms:[/dim]   {', '.join(t.platforms)}",
        f"[dim]Online:[/dim]      {t.hours_online}h/day    "
        f"[dim]Apps/day:[/dim] {t.apps_per_day}",
        "",
        f"[dim]Decision style:[/dim]       {b.decision_style.value.title()}",
        f"[dim]Risk tolerance:[/dim]       {b.risk_tolerance.value.title()}",
        f"[dim]Goal orientation:[/dim]     {b.goal_orientation.value.title()}",
        f"[dim]Frustration threshold:[/dim] {b.frustration_threshold.value.title()}",
        f"[dim]Adoption pattern:[/dim]     {b.adoption_pattern.value.title()}",
        "",
        f"[dim]Availability:[/dim]         {r.availability}",
        f"[dim]Preferred method:[/dim]     {r.preferred_method.value.title()}",
        f"[dim]Prior research exp:[/dim]   "
        f"{'[green]Yes[/green]' if r.prior_research_experience else '[dim]No[/dim]'}",
    ]

    if p.contradictions:
        lines.append("")
        lines.append("[yellow bold]Behavioural tensions:[/yellow bold]")
        for c in p.contradictions:
            lines.append(f"  [yellow]⚡[/yellow] {c.description}")

    if p.narrative:
        lines.append("")
        lines.append(f"[italic]{p.narrative}[/italic]")

    if p.tags:
        lines.append("")
        lines.append("[dim]Tags: " + "  ".join(f"#{t}" for t in p.tags) + "[/dim]")

    console.print(
        Panel(
            "\n".join(lines),
            title=title,
            border_style="blue",
            padding=(0, 1),
        )
    )
    console.print()


# ── CLI group ─────────────────────────────────────────────────────────────────

@click.group()
@click.version_option(package_name="synthetic-participants")
def cli() -> None:
    """synthetic-participants — generate richly profiled synthetic UX research participants."""


# ── generate command ──────────────────────────────────────────────────────────

@cli.command("generate")
@click.option("--n", default=5, show_default=True, help="Number of participants to generate.")
@click.option("--age-min", default=18, show_default=True, help="Minimum participant age.")
@click.option("--age-max", default=65, show_default=True, help="Maximum participant age.")
@click.option(
    "--digital-literacy",
    type=click.Choice(["novice", "intermediate", "advanced", "expert"]),
    default=None,
    help="Fix digital literacy level for all participants.",
)
@click.option("--occupation", default=None, help="Fix occupation for all participants.")
@click.option("--seed", default=None, type=int, help="Random seed for reproducibility.")
@click.option(
    "--llm-backend",
    type=click.Choice(["anthropic", "openai", "gemini"]),
    default=None,
    help="Optional LLM backend for narrative enrichment. Requires API key env var.",
)
@click.option("--llm-model", default=None, help="Override the default model for the chosen backend.")
@click.option("--json-output", is_flag=True, help="Output as JSON (CI/pipeline-friendly).")
def generate_cmd(
    n: int,
    age_min: int,
    age_max: int,
    digital_literacy: Optional[str],
    occupation: Optional[str],
    seed: Optional[int],
    llm_backend: Optional[str],
    llm_model: Optional[str],
    json_output: bool,
) -> None:
    """Generate a panel of synthetic UX research participants."""
    if age_min >= age_max:
        console.print("[red]--age-min must be less than --age-max[/red]")
        sys.exit(1)

    dl = DigitalLiteracy(digital_literacy) if digital_literacy else None

    panel = generate_panel(
        n=n,
        age_range=(age_min, age_max),
        occupation=occupation,
        digital_literacy=dl,
        seed=seed,
    )

    if llm_backend:
        from .profiler import enrich_panel

        if not json_output:
            console.print(
                f"[dim]Enriching {n} participant(s) with {llm_backend} narratives…[/dim]\n"
            )
        panel, errors = enrich_panel(panel, backend=llm_backend, model=llm_model)
        if errors and not json_output:
            for err in errors:
                console.print(f"[yellow]⚠ LLM enrichment failed: {err}[/yellow]")

    if json_output:
        click.echo(json.dumps([p.to_dict() for p in panel], indent=2))
        return

    console.print(
        f"\n[bold]Generated {len(panel)} synthetic participant(s)[/bold]"
        + (f"  [dim]seed={seed}[/dim]" if seed is not None else "")
        + "\n"
    )
    for p in panel:
        _print_participant(p)


# ── single command ────────────────────────────────────────────────────────────

@cli.command("single")
@click.argument("participant_id")
@click.option("--age-min", default=18, show_default=True)
@click.option("--age-max", default=65, show_default=True)
@click.option("--seed", default=None, type=int)
@click.option(
    "--llm-backend",
    type=click.Choice(["anthropic", "openai", "gemini"]),
    default=None,
)
@click.option("--llm-model", default=None)
@click.option("--json-output", is_flag=True)
def single_cmd(
    participant_id: str,
    age_min: int,
    age_max: int,
    seed: Optional[int],
    llm_backend: Optional[str],
    llm_model: Optional[str],
    json_output: bool,
) -> None:
    """Generate and display a single participant by PARTICIPANT_ID."""
    p = generate_participant(
        age_range=(age_min, age_max),
        seed=seed,
        participant_id=participant_id,
    )

    if llm_backend:
        from .profiler import enrich_with_narrative

        p = enrich_with_narrative(p, backend=llm_backend, model=llm_model)

    if json_output:
        click.echo(json.dumps(p.to_dict(), indent=2))
        return

    _print_participant(p)


# ── diversity command ─────────────────────────────────────────────────────────

@cli.command("diversity")
@click.option("--n", default=20, show_default=True, help="Panel size to evaluate.")
@click.option("--age-min", default=18, show_default=True)
@click.option("--age-max", default=65, show_default=True)
@click.option("--seed", default=42, show_default=True)
@click.option("--json-output", is_flag=True)
def diversity_cmd(
    n: int,
    age_min: int,
    age_max: int,
    seed: int,
    json_output: bool,
) -> None:
    """Print a diversity summary for a generated panel."""
    panel = generate_panel(n=n, age_range=(age_min, age_max), seed=seed)
    report = diversity_report(panel)

    if json_output:
        click.echo(json.dumps(report, indent=2))
        return

    console.print(f"\n[bold]Diversity report — {n} participants[/bold]  [dim]seed={seed}[/dim]\n")

    # Age
    console.print(
        f"  Age:  min={report['age']['min']}  max={report['age']['max']}  "
        f"mean={report['age']['mean']}"
    )
    console.print(
        f"  Participants with behavioural contradictions: "
        f"[yellow]{report['participants_with_contradictions']}[/yellow] / {n}"
    )
    console.print()

    def _table(title: str, data: dict) -> Table:
        tbl = Table(title=title, box=box.SIMPLE, show_header=True, header_style="bold")
        tbl.add_column("Value", style="dim")
        tbl.add_column("Count", justify="right")
        tbl.add_column("Share", justify="right")
        total = sum(data.values())
        for k, v in data.items():
            tbl.add_row(k, str(v), f"{v / total:.0%}")
        return tbl

    console.print(_table("Gender", report["gender_distribution"]))
    console.print(_table("Digital Literacy", report["digital_literacy_distribution"]))
    console.print(_table("Adoption Pattern", report["adoption_pattern_distribution"]))
