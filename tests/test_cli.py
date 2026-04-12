"""Tests for the CLI layer."""

import json

import pytest
from click.testing import CliRunner

from synthetic_participants.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


# ── generate command ──────────────────────────────────────────────────────────

def test_generate_runs(runner):
    result = runner.invoke(cli, ["generate", "--n", "2", "--seed", "1"])
    assert result.exit_code == 0


def test_generate_json_output_valid(runner):
    result = runner.invoke(cli, ["generate", "--n", "3", "--seed", "42", "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)
    assert len(data) == 3


def test_generate_json_fields_present(runner):
    result = runner.invoke(cli, ["generate", "--n", "1", "--seed", "0", "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    p = data[0]
    assert "participant_id" in p
    assert "demographics" in p
    assert "tech_profile" in p
    assert "behavioral_traits" in p
    assert "research_context" in p
    assert "contradictions" in p
    assert "narrative" in p
    assert "tags" in p


def test_generate_json_narrative_null_without_llm(runner):
    result = runner.invoke(cli, ["generate", "--n", "1", "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["narrative"] is None


def test_generate_json_enums_serialised_as_strings(runner):
    result = runner.invoke(cli, ["generate", "--n", "1", "--seed", "7", "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    tech = data[0]["tech_profile"]
    assert isinstance(tech["digital_literacy"], str)
    traits = data[0]["behavioral_traits"]
    assert isinstance(traits["decision_style"], str)
    assert isinstance(traits["risk_tolerance"], str)


def test_generate_age_range(runner):
    result = runner.invoke(
        cli,
        ["generate", "--n", "5", "--age-min", "25", "--age-max", "30", "--json-output"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    for p in data:
        assert 25 <= p["demographics"]["age"] <= 30


def test_generate_invalid_age_range(runner):
    result = runner.invoke(cli, ["generate", "--age-min", "50", "--age-max", "30"])
    assert result.exit_code != 0 or "must be less than" in result.output


def test_generate_fixed_digital_literacy(runner):
    result = runner.invoke(
        cli,
        ["generate", "--n", "3", "--digital-literacy", "expert", "--json-output"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    for p in data:
        assert p["tech_profile"]["digital_literacy"] == "expert"


def test_generate_fixed_occupation(runner):
    result = runner.invoke(
        cli,
        ["generate", "--n", "3", "--occupation", "Nurse", "--json-output"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    for p in data:
        assert p["demographics"]["occupation"] == "Nurse"


def test_generate_seed_reproducible(runner):
    r1 = runner.invoke(cli, ["generate", "--n", "3", "--seed", "99", "--json-output"])
    r2 = runner.invoke(cli, ["generate", "--n", "3", "--seed", "99", "--json-output"])
    assert json.loads(r1.output) == json.loads(r2.output)


def test_generate_different_seeds_differ(runner):
    r1 = runner.invoke(cli, ["generate", "--n", "5", "--seed", "1", "--json-output"])
    r2 = runner.invoke(cli, ["generate", "--n", "5", "--seed", "2", "--json-output"])
    d1 = json.loads(r1.output)
    d2 = json.loads(r2.output)
    ages1 = [p["demographics"]["age"] for p in d1]
    ages2 = [p["demographics"]["age"] for p in d2]
    assert ages1 != ages2


def test_generate_n_one(runner):
    result = runner.invoke(cli, ["generate", "--n", "1", "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == 1


def test_generate_n_ten(runner):
    result = runner.invoke(cli, ["generate", "--n", "10", "--json-output"])
    assert result.exit_code == 0
    assert len(json.loads(result.output)) == 10


def test_generate_ids_unique(runner):
    result = runner.invoke(cli, ["generate", "--n", "10", "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    ids = [p["participant_id"] for p in data]
    assert len(ids) == len(set(ids))


def test_generate_rich_output_no_crash(runner):
    """Terminal (non-JSON) output should not raise."""
    result = runner.invoke(cli, ["generate", "--n", "2", "--seed", "5"])
    assert result.exit_code == 0


# ── single command ────────────────────────────────────────────────────────────

def test_single_json_output(runner):
    result = runner.invoke(cli, ["single", "PTEST01", "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["participant_id"] == "PTEST01"


def test_single_correct_id(runner):
    result = runner.invoke(cli, ["single", "MY_ID", "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["participant_id"] == "MY_ID"


def test_single_seed_reproducible(runner):
    r1 = runner.invoke(cli, ["single", "P42", "--seed", "7", "--json-output"])
    r2 = runner.invoke(cli, ["single", "P42", "--seed", "7", "--json-output"])
    assert json.loads(r1.output) == json.loads(r2.output)


def test_single_narrative_null_without_llm(runner):
    result = runner.invoke(cli, ["single", "P_X", "--json-output"])
    assert result.exit_code == 0
    assert json.loads(result.output)["narrative"] is None


def test_single_rich_output(runner):
    result = runner.invoke(cli, ["single", "P_RICH", "--seed", "3"])
    assert result.exit_code == 0


# ── diversity command ─────────────────────────────────────────────────────────

def test_diversity_json_output(runner):
    result = runner.invoke(cli, ["diversity", "--n", "20", "--seed", "0", "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["n"] == 20
    assert "age" in data
    assert "gender_distribution" in data


def test_diversity_json_gender_totals(runner):
    result = runner.invoke(cli, ["diversity", "--n", "10", "--seed", "0", "--json-output"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    total = sum(data["gender_distribution"].values())
    assert total == 10


def test_diversity_json_age_stats_valid(runner):
    result = runner.invoke(
        cli,
        ["diversity", "--n", "20", "--age-min", "20", "--age-max", "30", "--seed", "0", "--json-output"],
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["age"]["min"] >= 20
    assert data["age"]["max"] <= 30


def test_diversity_rich_output(runner):
    result = runner.invoke(cli, ["diversity", "--n", "10", "--seed", "1"])
    assert result.exit_code == 0


# ── help texts ────────────────────────────────────────────────────────────────

def test_help_root(runner):
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "generate" in result.output


def test_help_generate(runner):
    result = runner.invoke(cli, ["generate", "--help"])
    assert result.exit_code == 0
    assert "--n" in result.output
    assert "--llm-backend" in result.output


def test_help_single(runner):
    result = runner.invoke(cli, ["single", "--help"])
    assert result.exit_code == 0


def test_help_diversity(runner):
    result = runner.invoke(cli, ["diversity", "--help"])
    assert result.exit_code == 0
