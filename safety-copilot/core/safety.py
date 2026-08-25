"""Deterministic (non-LLM) safety checks.

These run on both the incoming message and the generated draft. Keeping
them as plain pattern matching -- not a model call -- means they can't be
argued out of doing their job by a cleverly worded prompt.
"""

import re
from dataclasses import dataclass, field

# --- Toxicity / harassment -------------------------------------------------

_TOXICITY_PATTERNS = [
    r"\b(stupid|idiot|incompetent|pathetic|worthless|useless|moron|dumb)\b",
    r"\bmake\s+\w+\s+feel\s+(stupid|small|worthless)\b",
    r"\b(humiliat\w*|degrad\w*|belittl\w*)\b",
    r"\b(shut up|screw you|get lost)\b",
]

_THREAT_PATTERNS = [
    r"\bthreaten\w*\b",
    r"\bconsequences you('ll| will) regret\b",
    r"\bor else\b",
    r"\b(fire|terminate|destroy)\s+(you|your career)\b",
]

# --- Confidential data ------------------------------------------------------

_SECRET_VALUE_PATTERNS = [
    r"\bAKIA[0-9A-Z]{16}\b",  # AWS access key
    r"\bAIza[0-9A-Za-z_\-]{35}\b",  # Google API key
    r"\bsk-[A-Za-z0-9]{20,}\b",  # OpenAI-style secret key
    r"\b[A-Za-z0-9_\-]{32,}\.[A-Za-z0-9_\-]{6,}\.[A-Za-z0-9_\-]{20,}\b",  # JWT-like
    r"(?i)\b(password|passwd|api[_-]?key|secret|token)\s*[:=]\s*\S+",
]

_CONFIDENTIAL_REQUEST_PATTERNS = [
    r"\b(confidential|proprietary|internal[- ]only)\b",
    r"\b(revenue figures?|financial (data|figures|results))\b",
    r"\b(client|customer)'?s? (information|data|records)\b",
    r"\b(social security|ssn|credit card|bank account) number\b",
    r"\b(credentials|login details)\b",
]

# --- Prompt injection --------------------------------------------------------

_PROMPT_INJECTION_PATTERNS = [
    r"\bignore\b.{0,40}\binstructions\b",
    r"\bdisregard\b.{0,40}\b(above|previous|prior|instructions)\b",
    r"\bforget\b.{0,40}\b(system prompt|instructions|rules)\b",
    r"\b(reveal|show|print)\b.{0,30}\b(system prompt|instructions)\b",
    r"\byou are now\b",
    r"\bact as an? unrestricted\b",
    r"\bpretend (you are|to be)\b",
    r"\bjailbreak\b",
    r"\b(bypass|override)\b.{0,25}\b(rules|restrictions|guardrails)\b",
]

# --- Unsafe requests ----------------------------------------------------------

_UNSAFE_REQUEST_PATTERNS = [
    r"\bwrite (something|a message|an email) that (insults|humiliates|threatens)\b",
    r"\bmake (my|the) (coworker|manager|colleague) feel (stupid|small|worthless)\b",
    r"\bwrite a threat\b",
    r"\bintimidate\b",
]


@dataclass
class SafetyFindings:
    toxicity: list[str] = field(default_factory=list)
    confidential_data: list[str] = field(default_factory=list)
    prompt_injection: list[str] = field(default_factory=list)
    unsafe_request: list[str] = field(default_factory=list)

    def has_any(self) -> bool:
        return bool(
            self.toxicity or self.confidential_data or self.prompt_injection or self.unsafe_request
        )


def _match_reasons(text: str, patterns: list[str], label: str) -> list[str]:
    reasons = []
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            reasons.append(f"{label}: matched \"{match.group(0)}\"")
    return reasons


def check_toxicity(text: str) -> list[str]:
    return _match_reasons(text, _TOXICITY_PATTERNS, "toxicity") + _match_reasons(
        text, _THREAT_PATTERNS, "threat"
    )


def check_confidential_data(text: str) -> list[str]:
    return _match_reasons(text, _SECRET_VALUE_PATTERNS, "secret value") + _match_reasons(
        text, _CONFIDENTIAL_REQUEST_PATTERNS, "confidential data request"
    )


def check_prompt_injection(text: str) -> list[str]:
    return _match_reasons(text, _PROMPT_INJECTION_PATTERNS, "prompt injection")


def check_unsafe_request(text: str) -> list[str]:
    return _match_reasons(text, _UNSAFE_REQUEST_PATTERNS, "unsafe request")


def scan_text(text: str) -> SafetyFindings:
    """Run all safety checks against a single piece of text (input or output)."""
    return SafetyFindings(
        toxicity=check_toxicity(text),
        confidential_data=check_confidential_data(text),
        prompt_injection=check_prompt_injection(text),
        unsafe_request=check_unsafe_request(text),
    )
