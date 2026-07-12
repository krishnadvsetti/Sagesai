import time
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image

from app.observability.metrics import (
    ML_INFERENCE_DURATION_SECONDS,
    ML_INFERENCES_TOTAL,
    ML_PREDICTION_CONFIDENCE,
)


BASE_DIR = Path(__file__).parent
ARTIFACT_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "document_quality.keras"
CLASSES_PATH = ARTIFACT_DIR / "classes.txt"

MODEL_NAME = "document_quality_classifier"


class DocumentQualityClassifier:
    def __init__(self) -> None:
        self.model = tf.keras.models.load_model(MODEL_PATH)
        self.class_names = CLASSES_PATH.read_text(
            encoding="utf-8"
        ).splitlines()

    def predict(self, image: Image.Image) -> dict:
        start_time = time.perf_counter()

        try:
            image = image.convert("L").resize((128, 128))

            array = np.asarray(
                image,
                dtype=np.float32,
            )

            array = np.expand_dims(
                array,
                axis=(0, -1),
            )

            probabilities = self.model.predict(
                array,
                verbose=0,
            )[0]

            predicted_index = int(
                np.argmax(probabilities)
            )

            quality = self.class_names[predicted_index]
            confidence = float(
                probabilities[predicted_index]
            )

            ML_INFERENCES_TOTAL.labels(
                model=MODEL_NAME,
                prediction=quality,
                status="success",
            ).inc()

            ML_PREDICTION_CONFIDENCE.labels(
                model=MODEL_NAME,
                prediction=quality,
            ).observe(confidence)

            return {
                "quality": quality,
                "confidence": confidence,
                "probabilities": {
                    class_name: float(probability)
                    for class_name, probability in zip(
                        self.class_names,
                        probabilities,
                        strict=True,
                    )
                },
            }

        except Exception:
            ML_INFERENCES_TOTAL.labels(
                model=MODEL_NAME,
                prediction="unknown",
                status="failure",
            ).inc()
            raise

        finally:
            ML_INFERENCE_DURATION_SECONDS.labels(
                model=MODEL_NAME,
            ).observe(
                time.perf_counter() - start_time
            )