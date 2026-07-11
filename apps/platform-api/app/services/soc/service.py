from app.schemas.soc import SecurityEventRequest
from app.services.ai.gateway import AIGateway


class SOCAnalystService:
    def __init__(self) -> None:
        self.ai_gateway = AIGateway()

    def calculate_risk_score(
        self,
        event: SecurityEventRequest,
    ) -> int:
        text = (
            f"{event.event_type} {event.description}"
        ).lower()

        score = 20

        high_risk_terms = {
            "ransomware": 50,
            "malware": 30,
            "privilege escalation": 35,
            "data exfiltration": 45,
            "credential theft": 35,
            "brute force": 20,
            "unauthorized access": 25,
        }

        for term, weight in high_risk_terms.items():
            if term in text:
                score += weight

        return min(score, 100)

    @staticmethod
    def severity_from_score(
        score: int,
    ) -> str:
        if score >= 80:
            return "critical"
        if score >= 60:
            return "high"
        if score >= 30:
            return "medium"
        return "low"

    async def analyze(
        self,
        event: SecurityEventRequest,
    ) -> dict:
        risk_score = self.calculate_risk_score(event)
        severity = self.severity_from_score(risk_score)

        prompt = f"""
Analyze this security event as a SOC analyst.

Event type: {event.event_type}
Source IP: {event.source_ip or "Not provided"}
Destination IP: {event.destination_ip or "Not provided"}
Username: {event.username or "Not provided"}
Description: {event.description}

Preliminary risk score: {risk_score}/100
Preliminary severity: {severity}

Provide:
1. Incident summary
2. Likely threat category
3. Indicators requiring investigation
4. Relevant MITRE ATT&CK techniques, only when reasonably supported
5. Immediate containment recommendations
6. Investigation steps
7. False-positive considerations

Do not claim that an attack definitely occurred when evidence is insufficient.
"""

        analysis = await self.ai_gateway.generate(
            prompt=prompt,
            system_instruction=(
                "You are Sagesai's enterprise SOC cybersecurity analyst. "
                "Provide evidence-based security analysis and clearly distinguish "
                "observations, hypotheses, and recommended investigation steps."
            ),
        )

        return {
            "severity": severity,
            "risk_score": risk_score,
            "analysis": analysis,
        }