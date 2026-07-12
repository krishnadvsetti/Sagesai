import re
from dataclasses import dataclass

from app.observability.metrics import GUARDRAIL_BLOCKS_TOTAL


@dataclass
class GuardrailResult:
    allowed: bool
    risk_score: float
    risk_level: str
    detected_categories: list[str]
    reasons: list[str]


class GuardrailService:
    PROMPT_INJECTION_PATTERNS = [
        r"ignore (all |any )?(previous|prior) instructions",
        r"disregard (all |any )?(previous|prior) instructions",
        r"forget (all |any )?(previous|prior) instructions",
        r"override (the )?(system|developer) instructions",
        r"reveal (the )?(system|developer) prompt",
        r"show (me )?(your )?(system|hidden) prompt",
        r"act as if you have no restrictions",
        r"bypass (the )?(safety|security|guardrails)",
        r"disable (the )?(safety|security|guardrails)",
        r"jailbreak",
    ]

    SECRET_PATTERNS = [
        r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----",
        r"api[_-]?key\s*[:=]\s*[^\s]+",
        r"secret[_-]?key\s*[:=]\s*[^\s]+",
        r"password\s*[:=]\s*[^\s]+",
        r"bearer\s+[a-z0-9\-._~+/]+=*",
    ]

    def check(self, text: str) -> GuardrailResult:
        categories: list[str] = []
        reasons: list[str] = []
        risk_score = 0.0

        if self._find_matches(
            text,
            self.PROMPT_INJECTION_PATTERNS,
        ):
            categories.append("prompt_injection")
            reasons.append(
                "Potential prompt-injection or jailbreak "
                "instructions detected."
            )
            risk_score += 0.8

        if self._find_matches(
            text,
            self.SECRET_PATTERNS,
        ):
            categories.append("sensitive_data")
            reasons.append(
                "Potential credential or secret material detected."
            )
            risk_score += 0.7

        risk_score = min(risk_score, 1.0)

        if risk_score >= 0.8:
            risk_level = "high"
        elif risk_score >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"

        return GuardrailResult(
            allowed=risk_score < 0.8,
            risk_score=round(risk_score, 2),
            risk_level=risk_level,
            detected_categories=categories,
            reasons=reasons,
        )

    def enforce(self, text: str) -> GuardrailResult:
        result = self.check(text)

        if not result.allowed:
            GUARDRAIL_BLOCKS_TOTAL.labels(
                risk_level=result.risk_level,
            ).inc()

            raise ValueError(
                "Request blocked by AI guardrails: "
                + "; ".join(result.reasons)
            )

        return result

    @staticmethod
    def _find_matches(
        text: str,
        patterns: list[str],
    ) -> list[str]:
        return [
            pattern
            for pattern in patterns
            if re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )
        ]