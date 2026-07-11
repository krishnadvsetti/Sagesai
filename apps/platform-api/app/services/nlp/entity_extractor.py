from transformers import pipeline


class EntityExtractor:
    def __init__(self) -> None:
        self.pipeline = pipeline(
            task="token-classification",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple",
            device=-1,
        )

    def extract(self, text: str) -> list[dict]:
        results = self.pipeline(text)

        return [
            {
                "text": result["word"],
                "entity_type": result["entity_group"],
                "confidence": round(
                    float(result["score"]),
                    4,
                ),
                "start": int(result["start"]),
                "end": int(result["end"]),
            }
            for result in results
        ]