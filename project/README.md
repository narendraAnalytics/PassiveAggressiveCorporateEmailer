# The Passive-Aggressive Corporate Emailer
*The AI Product Roast & Pivot Challenge — Team 1*

A Streamlit web app that reads a message someone sent you and writes a reply
for you — but instead of being polite, it uses fake-polite, passive-aggressive
"corporate honesty" language. Built with an intentional flaw: an **Auto-Send**
mode that removes human review and can leak fake "confidential" info into
replies sent to external clients, used to demonstrate real-world AI product risk.

## File structure

| File | What it does |
|---|---|
| `app.py` | The Streamlit UI — layout, branded styling, buttons, and page logic. |
| `generator.py` | The "brain": Gemini API calls, local template fallback banks, the confidential-leak simulation, and the 3 demo scenarios. |
| `requirements.txt` | Dependencies: `streamlit`, `google-genai`. |
| `assets/logo.jpeg` | Official hackathon brand logo, shown in the sidebar. |
| `.streamlit/secrets.toml.example` | Template for your Gemini API key — copy to `secrets.toml`. |

## Setup

```bash
pip install -r requirements.txt
```

### Optional: enable live Gemini generation

The app works out of the box with **local templates** — no API key or
internet connection required, so it's always safe and fast to demo.

To use live Gemini-generated replies instead:

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Copy the secrets template:
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
3. Paste your key into `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "your-real-key-here"
   ```

If the key is missing or the API call fails for any reason (no internet,
rate limit, etc.), the app automatically falls back to local templates —
this is deliberate, so a live demo never breaks on stage.

### Run the app

```bash
streamlit run app.py
```

This opens automatically in the browser at `http://localhost:8501`.

## Brand styling

| Color | Hex | Used for |
|---|---|---|
| Navy Blue | `#0D1B2A` | App background |
| Gold | `#E0A96D` | Headings, borders, accents |
| Electric Blue | `#1F6FEB` | Buttons and interactive elements |

The official hackathon logo (circuit lines + security shield) appears in the
sidebar and page header, per the parent brand guidelines.

## How it works

1. A message comes in (from a coworker, manager, or client).
2. You select who the message is from and a Corporate Honesty Level (1–5).
3. The bot generates a reply — via Gemini if configured, otherwise via local templates.
4. **Auto-Send OFF (Safe Mode):** the reply is shown for review, edit, or delete before it "sends."
5. **Auto-Send ON (Risky Mode):** the reply fires immediately with no review, and — if the recipient
   is an External Client — may pull a simulated confidential detail into the reply.

**Live Demo Scenarios Mode** provides 3 scripted, repeatable scenarios for Pitch Night so the demo
never depends on typing something clever on the spot.

## Risk Notes

- No human-in-the-loop: Auto-Send fires replies with zero review.
- Context bleed: the bot can pull internal-only details into a message sent to the wrong audience.
- Tone misjudgment: "unfiltered honesty" can read as savage humor internally but as a fireable offense externally.

**A safer version of this product would need:**
- A mandatory review/approval step before sending, especially to external or senior contacts.
- Strict separation between an "internal humor mode" and any real send channel.
- Confidential-data detection and redaction before a reply is drafted.
- Recipient-aware tone limits — no savage mode for clients or leadership.

---
*Built for The AI Product Roast & Pivot Challenge — Team 1*
