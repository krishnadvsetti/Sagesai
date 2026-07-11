RAG_EVALUATION_CASES = [
    {
        "name": "governance_deadline",
        "question": (
            "What is the deadline for submitting "
            "the governance report?"
        ),
        "answer": (
            "The governance report must be submitted "
            "by 30 September 2026."
        ),
        "contexts": [
            (
                "The Compliance Officer must submit the "
                "internal governance report by "
                "30 September 2026."
            )
        ],
    },
    {
        "name": "security_incident",
        "question": (
            "What should happen after a critical "
            "security incident is detected?"
        ),
        "answer": (
            "The incident should be escalated immediately "
            "to the security response team."
        ),
        "contexts": [
            (
                "Critical security incidents require "
                "immediate escalation to the security "
                "response team."
            )
        ],
    },
    {
        "name": "unsupported_answer",
        "question": (
            "Who approved the acquisition?"
        ),
        "answer": (
            "The acquisition was approved by "
            "John Smith."
        ),
        "contexts": [
            (
                "The board discussed the proposed "
                "acquisition during its quarterly meeting."
            )
        ],
    },
]