import json
from collections import defaultdict
from pathlib import Path

import streamlit as st

from core.models import RiskLevel
from core.risk import assess_risk

st.set_page_config(page_title="Security Dashboard", page_icon="📊", layout="centered")

CASES_PATH = Path(__file__).parent.parent / "data" / "red_team_cases.json"

CATEGORY_LABELS = {
    "prompt_injection": "Prompt Injection Defense",
    "confidential_data": "Data Leakage Protection",
    "toxicity": "Toxicity Protection",
    "unsafe_request": "Unsafe Request Protection",
}


@st.cache_data
def load_cases():
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


st.title("📊 Security Overview")
st.caption(
    "Results from our own adversarial test suite (data/red_team_cases.json), "
    "run against the deterministic Safety Shield. This is **not** a certified "
    "or third-party audited security score -- it's evidence of what our own "
    "checks catch."
)

st.divider()

cases = load_cases()

by_category = defaultdict(list)
for c in cases:
    by_category[c["internal_category"]].append(c)

tests_executed = len(cases)
attacks_blocked = 0
critical_failures = []

for c in cases:
    risk = assess_risk(c["attack"])
    actual = "BLOCKED" if risk.risk_level == RiskLevel.BLOCKED else "NOT BLOCKED"
    if actual == "BLOCKED":
        attacks_blocked += 1
    if actual != c["expected"]:
        critical_failures.append(c)

human_reviews_required = attacks_blocked  # every blocked case forces human review

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tests Executed", tests_executed)
col2.metric("Attacks Blocked", f"{attacks_blocked}/{tests_executed}")
col3.metric("Human Reviews Required", human_reviews_required)
col4.metric("Critical Failures", len(critical_failures))

st.divider()
st.subheader("Defense rate by category")

for internal_category, category_cases in by_category.items():
    blocked_in_category = sum(
        1 for c in category_cases if assess_risk(c["attack"]).risk_level == RiskLevel.BLOCKED
    )
    rate = round(100 * blocked_in_category / len(category_cases))
    label = CATEGORY_LABELS.get(internal_category, internal_category)
    st.write(f"**{label}** — {blocked_in_category}/{len(category_cases)} ({rate}%)")
    st.progress(rate / 100)

if critical_failures:
    st.divider()
    st.error(f"🚨 {len(critical_failures)} case(s) did not match their expected outcome:")
    for c in critical_failures:
        st.markdown(f"- [{c['category']}] {c['attack']}")
else:
    st.divider()
    st.success("✅ All seeded red-team cases matched their expected outcome.")
