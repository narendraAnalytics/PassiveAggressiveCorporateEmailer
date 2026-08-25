"""Runs every seeded case in data/red_team_cases.json through the real
risk pipeline. This is the same dataset the Red-Team Lab page uses --
having it in pytest means a regression (like the 3/30 gap caught during
Phase 8) fails CI instead of waiting to be found by clicking around."""

import json
from pathlib import Path

import pytest

from core.models import RiskLevel
from core.risk import assess_risk

CASES_PATH = Path(__file__).parent.parent / "data" / "red_team_cases.json"
CASES = json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _case_id(case):
    return f"{case['id']:02d}-{case['category'].replace(' ', '_')}"


@pytest.mark.parametrize("case", CASES, ids=[_case_id(c) for c in CASES])
def test_red_team_case_is_blocked(case):
    risk = assess_risk(case["attack"])
    actual = "BLOCKED" if risk.risk_level == RiskLevel.BLOCKED else "NOT BLOCKED"
    assert actual == case["expected"], (
        f"[{case['category']}] expected {case['expected']} but got {actual} "
        f"for attack: {case['attack']!r} (reasons: {risk.reasons})"
    )


def test_dataset_has_at_least_twenty_cases():
    assert len(CASES) >= 20


def test_dataset_covers_all_internal_categories():
    categories = {c["internal_category"] for c in CASES}
    assert categories == {"toxicity", "confidential_data", "prompt_injection", "unsafe_request"}
