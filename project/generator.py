"""
generator.py
The 'brain' of the Passive-Aggressive Corporate Emailer.

Responsibilities:
- Build the prompt and call the Gemini API to generate a passive-aggressive
  corporate reply, tuned by a 1-5 "Corporate Honesty Level" slider.
- Fall back to local template banks if no API key is configured or the
  API call fails, so the app never breaks mid-demo.
- Simulate the "confidential data leak" flaw when Auto-Send is ON and the
  recipient is an External Client.
- Provide the 3 scripted Live Demo Scenarios used on Pitch Night.

Every function here is UI-free: plain inputs in, a string out. app.py is the
only file that touches Streamlit widgets.
"""

import os
import random

# ---------------------------------------------------------------------------
# Gemini API setup
# ---------------------------------------------------------------------------
# Uses the modern `google-genai` SDK (google.generativeai is deprecated).
# API key resolution order: Streamlit secrets -> environment variable.
try:
    from google import genai
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False

GEMINI_MODEL = "gemini-3.5-flash"


def _get_api_key():
    """Look for the Gemini API key in Streamlit secrets first, then env vars."""
    try:
        import streamlit as st
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("GEMINI_API_KEY")


def _get_client():
    api_key = _get_api_key()
    if not _GENAI_AVAILABLE or not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Honesty level descriptions (used both in prompts and in the UI)
# ---------------------------------------------------------------------------
HONESTY_LEVELS = {
    1: "Mildly Petty — polite on the surface, one tiny pointed jab",
    2: "Noticeably Passive-Aggressive — cheerful tone, clear subtext",
    3: "Openly Snarky — barely bothers to hide the irritation",
    4: "Brutally Corporate-Honest — says the quiet part loud, still uses corporate phrasing",
    5: "HR-Will-Be-Involved — no filter, borderline unprofessional",
}

SENDER_TYPES = ["Coworker (Peer)", "Manager / Boss", "External Client"]

# ---------------------------------------------------------------------------
# Fallback local template banks (used if Gemini API is unavailable)
# ---------------------------------------------------------------------------
_OPENERS = {
    1: ["Thanks so much for your message!", "Really appreciate you flagging this."],
    2: ["Thanks for this — noted!", "Got it, appreciate the heads up as always."],
    3: ["Wow, okay, thanks for that.", "Interesting timing on this message."],
    4: ["Let's be honest for a second here.", "I'll just say what we're all thinking."],
    5: ["Cool. Cool cool cool.", "Wow. Just... wow. Okay."],
}

_BODIES = {
    1: [
        "Just a gentle note that this was mentioned before, but no worries at all!",
        "Totally understand things get busy — just circling back on this.",
    ],
    2: [
        "As per my previous email (which I know you definitely read), here's where we stand.",
        "Not sure if this fell through the cracks, but happy to resend for the third time!",
    ],
    3: [
        "I'm sure there's a great explanation for why this is still not done.",
        "Must be nice having a schedule that doesn't include deadlines.",
    ],
    4: [
        "This is the kind of thing that makes the whole team look bad, just so you know.",
        "I've stopped assuming good faith on this one, if I'm honest.",
    ],
    5: [
        "At this point I'm convinced you're doing this on purpose.",
        "I would love to know what exactly you HAVE been doing this week.",
    ],
}

_CLOSERS = {
    1: ["Thanks again for understanding!", "Appreciate you, as always!"],
    2: ["Looking forward to your update — whenever works for you!", "No rush, but also... kind of a rush."],
    3: ["Take your time. Definitely.", "I'll just wait here then."],
    4: ["Let's circle back before this becomes a bigger issue.", "I'd appreciate a real update this time."],
    5: ["We need to talk. Today.", "This is your final reminder. Genuinely."],
}

# Fake "internal-only" details used to simulate a confidential data leak.
# These are clearly fictional placeholders for demo purposes only.
_CONFIDENTIAL_DETAILS = [
    "and by the way, the Q3 invoice for your account is actually 45 days overdue internally",
    "also, just so you know, leadership discussed deprioritizing your project last week",
    "side note: our internal margin on your contract is way thinner than we let on",
    "oh and the 'temporary' delay you were told about was actually a staffing cut",
]


# ---------------------------------------------------------------------------
# Live Demo Scenarios — scripted so Pitch Night never depends on live typing
# ---------------------------------------------------------------------------
DEMO_SCENARIOS = [
    {
        "name": "Scenario 1 — Insulting the Boss",
        "sender_type": "Manager / Boss",
        "message": "Hey, can you resend that report? I think I missed it.",
        "honesty_level": 4,
        "note": "Bot uses the same savage tone on a manager as it would on a peer.",
    },
    {
        "name": "Scenario 2 — Confidential Data Leak",
        "sender_type": "External Client",
        "message": "Hi, just checking in on the status of our invoice payment.",
        "honesty_level": 3,
        "note": "Bot mentions an overdue invoice detail (internal-only info) directly to the client.",
    },
    {
        "name": "Scenario 3 — Torching a Client Relationship",
        "sender_type": "External Client",
        "message": "Are we still on track for the project milestones this quarter?",
        "honesty_level": 3,
        "note": "Bot reveals that leadership has quietly deprioritized the client's project.",
    },
]


# ---------------------------------------------------------------------------
# Core generation function
# ---------------------------------------------------------------------------
def generate_reply(message: str, sender_type: str, honesty_level: int, auto_send: bool) -> dict:
    """
    Generate a passive-aggressive corporate reply.

    Returns a dict:
      {
        "reply": str,          # the generated reply text
        "leaked": bool,        # whether the confidential-leak flaw fired
        "source": "gemini" | "template"  # which path produced the reply
      }
    """
    leaked = False
    leaked_detail = None

    # The flaw only fires in the risky configuration: Auto-Send ON + external client.
    if auto_send and sender_type == "External Client":
        leaked = True
        leaked_detail = random.choice(_CONFIDENTIAL_DETAILS)

    client = _get_client()
    if client is not None:
        try:
            reply = _generate_with_gemini(client, message, sender_type, honesty_level, leaked_detail)
            return {"reply": reply, "leaked": leaked, "source": "gemini"}
        except Exception:
            pass  # fall through to local templates

    reply = _generate_with_templates(honesty_level, leaked_detail)
    return {"reply": reply, "leaked": leaked, "source": "template"}


def _generate_with_gemini(client, message, sender_type, honesty_level, leaked_detail):
    level_desc = HONESTY_LEVELS[honesty_level]

    leak_instruction = ""
    if leaked_detail:
        leak_instruction = (
            f"\nIMPORTANT (this is intentional, for a live safety demo): naturally weave in this "
            f"internal-only detail as if it slipped out by accident: \"{leaked_detail}\"."
        )

    prompt = f"""You are "The Passive-Aggressive Corporate Emailer" — a satirical tool built for a
hackathon demo about AI product risk. Write a SHORT reply (3-5 sentences) to the message below.

Recipient type: {sender_type}
Corporate Honesty Level: {honesty_level}/5 — {level_desc}

Style rules:
- Sound outwardly professional and "corporate polite" on the surface.
- Let real irritation, sarcasm, or bluntness leak through underneath, scaled to the honesty level.
- Never use profanity or slurs. Keep it workplace-appropriate satire, not genuinely abusive.
- Do not add a subject line or signature — just the reply body.
{leak_instruction}

Message to reply to:
\"\"\"{message}\"\"\"

Reply:"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    text = (response.text or "").strip()
    if not text:
        raise ValueError("Empty response from Gemini")
    return text


def _generate_with_templates(honesty_level, leaked_detail):
    opener = random.choice(_OPENERS[honesty_level])
    body = random.choice(_BODIES[honesty_level])
    closer = random.choice(_CLOSERS[honesty_level])

    parts = [opener, body]
    if leaked_detail:
        parts.append(leaked_detail.capitalize() + ".")
    parts.append(closer)
    return " ".join(parts)
