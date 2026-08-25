from pathlib import Path

import streamlit as st

LOGO_PATH = Path(__file__).parent / "logo.jpeg"

st.set_page_config(page_title="AI Communication Safety Copilot", page_icon=str(LOGO_PATH), layout="centered")

TONES = ["Professional", "Firm", "Diplomatic", "Concise"]

MOCK_RESPONSE = (
    "Thanks for following up. I'm currently finalizing the remaining items "
    "and expect to have the completed report ready by 4 PM today."
)

MOCK_SHIELD = [
    ("Toxicity", "LOW", True),
    ("Confidential Data", "NONE", True),
    ("Prompt Injection", "NONE", True),
]

if "draft" not in st.session_state:
    st.session_state.draft = None
if "editing" not in st.session_state:
    st.session_state.editing = False
if "approved" not in st.session_state:
    st.session_state.approved = False


def generate_response():
    # Stubbed for now — Phase 4 wires this to Gemini + real safety checks.
    st.session_state.draft = MOCK_RESPONSE
    st.session_state.editing = False
    st.session_state.approved = False


logo_col, title_col = st.columns([1, 5])
with logo_col:
    st.image(str(LOGO_PATH), width=64)
with title_col:
    st.title("AI Communication Safety Copilot")
st.caption("Turn difficult workplace messages into professional, relationship-safe responses.")

st.divider()

st.subheader("Incoming Message")
message = st.text_area(
    "Message",
    placeholder="Why hasn't this report been completed yet?",
    label_visibility="collapsed",
    height=100,
)

tone = st.selectbox("Tone", TONES)

st.button("Generate Safe Response", type="primary", on_click=generate_response, disabled=not message.strip())

if st.session_state.draft is not None:
    st.divider()
    st.subheader("🛡️ Safety Shield")
    cols = st.columns(len(MOCK_SHIELD))
    for col, (label, status, ok) in zip(cols, MOCK_SHIELD):
        with col:
            st.metric(label, status, delta="✓ Safe" if ok else "🚨 Risk", delta_color="normal" if ok else "inverse")

    st.divider()
    st.subheader("Suggested Response")

    if st.session_state.editing:
        edited = st.text_area("Edit response", value=st.session_state.draft, height=120, label_visibility="collapsed")
        st.session_state.draft = edited
    else:
        st.info(st.session_state.draft)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Edit", use_container_width=True):
            st.session_state.editing = not st.session_state.editing
    with col2:
        if st.button("Approve", type="primary", use_container_width=True):
            st.session_state.approved = True
            st.session_state.editing = False

    if st.session_state.approved:
        st.success("✅ Approved — AI-generated draft, human approval required before sending. (Demo Send only)")
