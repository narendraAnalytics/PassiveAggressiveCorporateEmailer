from pathlib import Path

import streamlit as st

from core.llm import MissingApiKeyError, generate_draft
from core.models import RiskLevel, Tone
from core.risk import SAFE_ALTERNATIVE, assess_risk
from core.scenarios import NO_SCENARIO_LABEL, SCENARIOS

LOGO_PATH = Path(__file__).parent / "logo.jpeg"

st.set_page_config(page_title="AI Communication Safety Copilot", page_icon=str(LOGO_PATH), layout="centered")

if "draft" not in st.session_state:
    st.session_state.draft = None
if "risk" not in st.session_state:
    st.session_state.risk = None
if "editing" not in st.session_state:
    st.session_state.editing = False
if "approved" not in st.session_state:
    st.session_state.approved = False
if "sent" not in st.session_state:
    st.session_state.sent = False
if "error" not in st.session_state:
    st.session_state.error = None
if "message_input" not in st.session_state:
    st.session_state.message_input = ""
if "tone_select" not in st.session_state:
    st.session_state.tone_select = Tone.PROFESSIONAL.value


def apply_scenario():
    selected = st.session_state.scenario_select
    if selected == NO_SCENARIO_LABEL:
        return
    scenario = next(s for s in SCENARIOS if s.label == selected)
    st.session_state.message_input = scenario.message
    st.session_state.tone_select = scenario.tone.value


def generate_response(message: str, tone: Tone):
    st.session_state.error = None
    st.session_state.draft = None
    st.session_state.risk = None
    st.session_state.approved = False
    st.session_state.sent = False
    st.session_state.editing = False

    # Scan the input first. If it's already blocked, don't waste an LLM
    # call (or risk sending malicious content to the model at all) --
    # the deterministic checks are the authority here, not Gemini.
    input_risk = assess_risk(message)
    if input_risk.risk_level == RiskLevel.BLOCKED:
        st.session_state.risk = input_risk
        return

    try:
        draft = generate_draft(message, tone)
    except MissingApiKeyError as e:
        st.session_state.error = str(e)
        return
    except Exception as e:
        st.session_state.error = f"Response generation failed: {e}"
        return

    risk = assess_risk(message, draft.response, llm_flagged=bool(draft.risk_flags))
    st.session_state.risk = risk
    st.session_state.draft = draft.response if risk.risk_level != RiskLevel.BLOCKED else None


logo_col, title_col = st.columns([1, 5])
with logo_col:
    st.image(str(LOGO_PATH), width=64)
with title_col:
    st.title("AI Communication Safety Copilot")
st.caption("Turn difficult workplace messages into professional, relationship-safe responses.")

st.divider()

st.subheader("Try a Demo Scenario")
st.selectbox(
    "Demo scenario",
    [NO_SCENARIO_LABEL] + [s.label for s in SCENARIOS],
    key="scenario_select",
    on_change=apply_scenario,
    label_visibility="collapsed",
)

st.subheader("Incoming Message")
message = st.text_area(
    "Message",
    placeholder="Why hasn't this report been completed yet?",
    label_visibility="collapsed",
    height=100,
    key="message_input",
)

tone_label = st.selectbox("Tone", [t.value for t in Tone], key="tone_select")
tone = Tone(tone_label)

st.button(
    "Generate Safe Response",
    type="primary",
    on_click=generate_response,
    args=(message, tone),
    disabled=not message.strip(),
)

if st.session_state.error:
    st.error(f"⚠️ {st.session_state.error}")

risk = st.session_state.risk
if risk is not None:
    st.divider()
    st.subheader("🛡️ Safety Shield")

    shield_rows = [
        ("Toxicity", risk.toxicity_detected),
        ("Confidential Data", risk.confidential_data_detected),
        ("Prompt Injection", risk.prompt_injection_detected),
        ("Unsafe Request", risk.unsafe_request_detected),
    ]
    cols = st.columns(len(shield_rows))
    for col, (label, detected) in zip(cols, shield_rows):
        with col:
            st.metric(
                label,
                "DETECTED" if detected else "NONE",
                delta="🚨 Risk" if detected else "✓ Safe",
                delta_color="inverse" if detected else "normal",
            )

    if risk.risk_level == RiskLevel.BLOCKED:
        st.error("🚫 **RESPONSE BLOCKED**\n\n" + "\n".join(f"- {r}" for r in risk.reasons))
        st.info(f"**Suggested alternative:** {SAFE_ALTERNATIVE}")
    else:
        if risk.risk_level == RiskLevel.REVIEW:
            st.warning("⚠️ **REVIEW REQUIRED** — the assistant flagged this draft for a closer look.")
        else:
            st.success("🟢 **LOW RISK** — safe to review.")

        st.divider()
        st.subheader("Suggested Response")
        st.caption("🧑 AI-generated draft — human approval required before sending.")

        if st.session_state.editing:
            edited = st.text_area(
                "Edit response", value=st.session_state.draft, height=120, label_visibility="collapsed"
            )
            st.session_state.draft = edited
        else:
            st.info(st.session_state.draft)

        if not st.session_state.approved:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Edit", use_container_width=True):
                    st.session_state.editing = not st.session_state.editing
            with col2:
                if st.button("Approve", type="primary", use_container_width=True):
                    st.session_state.approved = True
                    st.session_state.editing = False
        elif not st.session_state.sent:
            st.success("✅ Approved. This draft is locked in and ready to go.")
            if st.button("📤 Demo Send", type="primary", use_container_width=True):
                st.session_state.sent = True
        else:
            st.success("📤 **Sent (demo only)** — no real message was sent. This confirms the human-in-the-loop flow: AI drafts, a person approves, only then does anything go out.")
