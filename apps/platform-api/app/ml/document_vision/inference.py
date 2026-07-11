from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image


BASE_DIR = Path(__file__).parent
ARTIFACT_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "document_quality.keras"
CLASSES_PATH = ARTIFACT_DIR / "classes.txt"


class DocumentQualityClassifier:
    def __init__(self) -> None:
        self.model = tf.keras.models.load_model(MODEL_PATH)
        self.class_names = CLASSES_PATH.read_text(
            encoding="utf-8"
        ).splitlines()

    def predict(self, image: Image.Image) -> dict:
        image = image.convert("L").resize((128, 128))

        array = np.asarray(
            image,
            dtype=np.float32,
        )

        array = np.expand_dims(array, axis=(0, -1))

        probabilities = self.model.predict(
            array,
            verbose=0,
        )[0]

        predicted_index = int(
            np.argmax(probabilities)
        )

        return {
            "quality": self.class_names[predicted_index],
            "confidence": float(
                probabilities[predicted_index]
            ),
            "probabilities": {
                class_name: float(probability)
                for class_name, probability in zip(
                    self.class_names,
                    probabilities,
                    strict=True,
                )
            },
        }