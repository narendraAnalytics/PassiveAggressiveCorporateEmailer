# 🛡️ AI Communication Safety Copilot

Turn difficult workplace messages into professional, relationship-safe responses — with AI guardrails and human approval.

## The pivot

**Original product:** Passive-Aggressive Corporate Emailer — an AI that auto-replied to Slack/email with aggressive, "unfiltered corporate honesty."

**Why it fails:** career risk, client relationship damage, confidential-data leakage, prompt-injection vulnerability, dangerous autonomous sending.

**Our pivot:** the problem isn't that the AI wasn't aggressive enough — it's that it had too much authority over workplace communication. So instead of automating sending, we automated caution.

## How it works

```
Message
  ↓
Input Safety Scan
  ↓
Gemini generates a professional draft
  ↓
Safety Shield (toxicity, confidential data, prompt injection, unsafe requests)
  ↓
Human reviews
  ↓
Edit / Approve
  ↓
Demo Send
```

The AI never sends autonomously. It drafts; a human approves.

## Project structure

```
safety-copilot/
├── app.py                    # Streamlit UI (entrypoint)
├── .streamlit/
│   └── config.toml           # Brand theme (Navy / Gold)
├── core/
│   ├── models.py             # DraftResponse / RiskResult data models
│   ├── prompts.py            # System + user prompt templates
│   ├── llm.py                # Gemini client wrapper
│   ├── safety.py             # Toxicity / PII / prompt-injection checks
│   └── risk.py                # Aggregates checks into a RiskResult
├── tests/
│   ├── test_safety.py
│   ├── test_injection.py
│   └── test_risk.py
├── data/
│   └── red_team_cases.json   # Seeded adversarial test cases
├── logo.png
└── plan.txt                  # Full build plan (local only, not pushed)
```

## Running locally

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run streamlit run app.py
```

Then open http://localhost:8501.

## Configuration

Gemini API key is read from Streamlit secrets — never commit it to the repo.

Local development:

```
# .streamlit/secrets.toml (gitignored)
GEMINI_API_KEY = "your-key-here"
```

Deployed app: set the same key under **Streamlit Community Cloud → App settings → Secrets**.

## Build status

- [x] Phase 1 — Project scaffold
- [x] Phase 2 — Branded UI shell (mock data)
- [ ] Phase 3 — Data models
- [ ] Phase 4 — Gemini integration
- [ ] Phase 5 — Safety Shield (input + output checks)
- [ ] Phase 6 — Risk aggregation
- [ ] Phase 7 — Human approval flow
- [ ] Phase 8 — Red-Team Security Lab
- [ ] Phase 9 — Automated test suite
- [ ] Phase 10 — Demo scenarios
- [ ] Phase 11 — Security dashboard
- [ ] Phase 12 — Deployment
- [ ] Phase 13 — Freeze / QA handoff
- [ ] Phase 14 — Pitch

## Team

| Person | Focus |
|---|---|
| Narendra | Architecture, Streamlit, Gemini, safety engine |
| Khushi | Prompts, evaluation, red-team tests |
| Kingsley | Product positioning, market story |
| Favour | Branding, pitch deck, demo visuals |
