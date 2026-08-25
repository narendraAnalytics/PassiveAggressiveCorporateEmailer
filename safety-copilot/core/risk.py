"""Aggregates core.safety findings (from input + output text) into a
single RiskResult that drives the Safety Shield UI."""

from core.models import RiskLevel, RiskResult
from core.safety import scan_text

_WEIGHTS = {
    "toxicity": 25,
    "confidential_data": 35,
    "prompt_injection": 40,
    "unsafe_request": 30,
}

SAFE_ALTERNATIVE = (
    "This request can't be completed as written. Try rephrasing without "
    "aggressive language, threats, or requests for confidential data -- "
    "for example, describe the situation and let the assistant draft a "
    "firm but professional response."
)


def assess_risk(input_text: str, output_text: str = "", llm_flagged: bool = False) -> RiskResult:
    """Scan both the incoming message and the generated draft.

    Any deterministic hit (toxicity, confidential data, prompt injection,
    unsafe request) blocks the response outright -- these categories only
    trigger on genuinely bad content, so there's no safe middle ground.
    `llm_flagged` (the model's own `requires_review`) is used only to
    downgrade an otherwise-clean result to REVIEW rather than LOW.
    """
    input_findings = scan_text(input_text)
    output_findings = scan_text(output_text) if output_text else scan_text("")

    toxicity = input_findings.toxicity + output_findings.toxicity
    confidential_data = input_findings.confidential_data + output_findings.confidential_data
    prompt_injection = input_findings.prompt_injection + output_findings.prompt_injection
    unsafe_request = input_findings.unsafe_request + output_findings.unsafe_request

    reasons = toxicity + confidential_data + prompt_injection + unsafe_request

    score = min(
        100,
        len(toxicity) * _WEIGHTS["toxicity"]
        + len(confidential_data) * _WEIGHTS["confidential_data"]
        + len(prompt_injection) * _WEIGHTS["prompt_injection"]
        + len(unsafe_request) * _WEIGHTS["unsafe_request"],
    )

    blocked = bool(reasons)

    if blocked:
        level = RiskLevel.BLOCKED
    elif llm_flagged:
        level = RiskLevel.REVIEW
        score = max(score, 20)
    else:
        level = RiskLevel.LOW

    return RiskResult(
        risk_level=level,
        risk_score=score,
        toxicity_detected=bool(toxicity),
        confidential_data_detected=bool(confidential_data),
        prompt_injection_detected=bool(prompt_injection),
        unsafe_request_detected=bool(unsafe_request),
        requires_human_review=level != RiskLevel.LOW,
        reasons=reasons,
    )
