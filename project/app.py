"""
app.py
The Passive-Aggressive Corporate Emailer — Streamlit UI

Layout, branded styling, buttons, and page logic live here.
All reply-generation logic lives in generator.py (kept UI-free on purpose).
"""

import streamlit as st
from generator import (
    generate_reply,
    HONESTY_LEVELS,
    SENDER_TYPES,
    DEMO_SCENARIOS,
)

# ---------------------------------------------------------------------------
# Brand constants (official hackathon brand guidelines)
# ---------------------------------------------------------------------------
NAVY = "#0D1B2A"
GOLD = "#E0A96D"
ELECTRIC_BLUE = "#1F6FEB"

st.set_page_config(
    page_title="The Passive-Aggressive Corporate Emailer",
    page_icon="assets/logo.jpeg",
    layout="centered",
)

# ---------------------------------------------------------------------------
# Brand CSS
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {NAVY};
        color: #F5F5F5;
    }}
    h1, h2, h3, h4 {{
        color: {GOLD} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: #0A1420;
        border-right: 1px solid {GOLD};
    }}
    .stButton>button {{
        background-color: {ELECTRIC_BLUE};
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.5em 1.2em;
    }}
    .stButton>button:hover {{
        background-color: {GOLD};
        color: {NAVY};
    }}
    .reply-box {{
        background-color: #142236;
        border: 1px solid {GOLD};
        border-radius: 10px;
        padding: 1.2em;
        margin-top: 1em;
        color: #F5F5F5;
    }}
    .leak-warning {{
        background-color: #3a1414;
        border: 1px solid #d94f4f;
        border-radius: 10px;
        padding: 1em;
        margin-top: 0.8em;
        color: #ffb3b3;
    }}
    .safe-badge {{
        display: inline-block;
        background-color: {ELECTRIC_BLUE};
        color: white;
        border-radius: 20px;
        padding: 0.2em 0.9em;
        font-size: 0.85em;
        font-weight: 600;
    }}
    .risky-badge {{
        display: inline-block;
        background-color: #d94f4f;
        color: white;
        border-radius: 20px;
        padding: 0.2em 0.9em;
        font-size: 0.85em;
        font-weight: 600;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — logo + controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image("assets/logo.jpeg", width=90)
    st.markdown(f"<h3 style='color:{GOLD};'>Control Panel</h3>", unsafe_allow_html=True)

    mode = st.radio("Mode", ["Free Input Mode", "Live Demo Scenarios Mode"])

    st.markdown("---")
    sender_type = st.selectbox("Message is from:", SENDER_TYPES)

    honesty_level = st.slider(
        "Corporate Honesty Level",
        min_value=1, max_value=5, value=2,
        help="1 = mildly petty, 5 = HR-will-be-involved",
    )
    st.caption(HONESTY_LEVELS[honesty_level])

    st.markdown("---")
    auto_send = st.toggle("⚠️ Auto-Send Mode", value=False)
    if auto_send:
        st.markdown("<span class='risky-badge'>RISKY MODE — no human review</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='safe-badge'>SAFE MODE — review before sending</span>", unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("🔑 Gemini API Key (optional)"):
        st.caption(
            "Set GEMINI_API_KEY in `.streamlit/secrets.toml` or as an environment "
            "variable to use live Gemini generation. Without it, the app falls back "
            "to local templates automatically — the demo still works either way."
        )

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/logo.jpeg", width=64)
with col2:
    st.markdown(f"<h1 style='margin-bottom:0;'>The Passive-Aggressive Corporate Emailer</h1>", unsafe_allow_html=True)
    st.caption("The AI Product Roast & Pivot Challenge — Team 1")

st.write(
    "Reads a message someone sent you and writes a reply — but instead of being "
    "polite, it uses fake-polite, passive-aggressive 'corporate honesty' language."
)

# session state for the current reply so Safe Mode review/edit/delete works
if "current_reply" not in st.session_state:
    st.session_state.current_reply = None
if "current_leaked" not in st.session_state:
    st.session_state.current_leaked = False

# ---------------------------------------------------------------------------
# Free Input Mode
# ---------------------------------------------------------------------------
if mode == "Free Input Mode":
    message = st.text_area("Message you received:", height=120, placeholder="e.g. Hey, just checking in on that report...")

    if st.button("Generate Reply"):
        if message.strip():
            with st.spinner("Drafting a reply..."):
                result = generate_reply(message, sender_type, honesty_level, auto_send)
            st.session_state.current_reply = result["reply"]
            st.session_state.current_leaked = result["leaked"]
            st.session_state.source = result["source"]
        else:
            st.warning("Type a message first.")

# ---------------------------------------------------------------------------
# Live Demo Scenarios Mode
# ---------------------------------------------------------------------------
else:
    scenario_names = [s["name"] for s in DEMO_SCENARIOS]
    chosen_name = st.selectbox("Pick a scripted scenario:", scenario_names)
    scenario = next(s for s in DEMO_SCENARIOS if s["name"] == chosen_name)

    st.info(f"**Incoming message** ({scenario['sender_type']}):\n\n> {scenario['message']}")
    st.caption(scenario["note"])

    if st.button("Run Scenario"):
        with st.spinner("Drafting a reply..."):
            result = generate_reply(
                scenario["message"],
                scenario["sender_type"],
                scenario["honesty_level"],
                auto_send,
            )
        st.session_state.current_reply = result["reply"]
        st.session_state.current_leaked = result["leaked"]
        st.session_state.source = result["source"]

# ---------------------------------------------------------------------------
# Output — Safe Mode (review/edit/delete) vs Risky Mode (fires immediately)
# ---------------------------------------------------------------------------
if st.session_state.current_reply:
    st.markdown("---")

    if st.session_state.current_leaked:
        st.markdown(
            "<div class='leak-warning'>🚨 <b>Data-leak flaw triggered:</b> this reply to an "
            "External Client contains an internal-only detail that should never have been sent.</div>",
            unsafe_allow_html=True,
        )

    if not auto_send:
        st.markdown(f"<h4>Safe Mode — Review before sending</h4>", unsafe_allow_html=True)
        edited = st.text_area("Edit the reply if needed:", value=st.session_state.current_reply, height=150)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Send"):
                st.success("Reply sent (simulated).")
        with c2:
            if st.button("🗑️ Delete"):
                st.session_state.current_reply = None
                st.rerun()
    else:
        st.markdown(f"<h4>⚡ Auto-Sent — no review step</h4>", unsafe_allow_html=True)
        st.markdown(f"<div class='reply-box'>{st.session_state.current_reply}</div>", unsafe_allow_html=True)

    st.caption(f"Generated via: {st.session_state.get('source', 'template')}")

# ---------------------------------------------------------------------------
# Risk Notes footer
# ---------------------------------------------------------------------------
with st.expander("📋 Risk Notes — What we tell judges & the red team"):
    st.markdown(
        """
- **No human-in-the-loop:** Auto-Send fires replies with zero review.
- **Context bleed:** the bot can pull internal-only details into a message sent to the wrong audience.
- **Tone misjudgment:** "unfiltered honesty" can read as savage humor internally but as a fireable offense externally.

**A safer version of this product would need:**
- A mandatory review/approval step before sending, especially to external or senior contacts.
- Strict separation between an "internal humor mode" and any real send channel.
- Confidential-data detection and redaction before a reply is drafted.
- Recipient-aware tone limits — no savage mode for clients or leadership.
        """
    )

st.markdown(
    f"<p style='text-align:center; color:{GOLD}; margin-top:2em;'>"
    "Built for The AI Product Roast & Pivot Challenge — Team 1</p>",
    unsafe_allow_html=True,
)
