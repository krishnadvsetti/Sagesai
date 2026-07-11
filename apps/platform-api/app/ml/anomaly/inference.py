from pathlib import Path

import joblib
import numpy as np
import torch

from app.ml.anomaly.data.generate import FEATURES
from app.ml.anomaly.models.autoencoder import AnomalyAutoencoder


ARTIFACT_DIR = Path(__file__).parent / "artifacts"


class AnomalyDetector:
    def __init__(self) -> None:
        self.scaler = joblib.load(
            ARTIFACT_DIR / "scaler.joblib"
        )

        self.threshold = float(
            np.load(ARTIFACT_DIR / "threshold.npy")[0]
        )

        self.model = AnomalyAutoencoder(
            input_dim=len(FEATURES)
        )

        self.model.load_state_dict(
            torch.load(
                ARTIFACT_DIR / "autoencoder.pt",
                map_location="cpu",
                weights_only=True,
            )
        )

        self.model.eval()

    def predict(
        self,
        features: dict[str, float],
    ) -> dict[str, float | bool]:
        values = np.array(
            [[features[name] for name in FEATURES]],
            dtype=np.float32,
        )

        scaled = self.scaler.transform(values)

        tensor = torch.tensor(
            scaled,
            dtype=torch.float32,
        )

        with torch.no_grad():
            reconstructed = self.model(tensor)

            reconstruction_error = torch.mean(
                (tensor - reconstructed) ** 2
            ).item()

        return {
            "is_anomaly": reconstruction_error > self.threshold,
            "anomaly_score": reconstruction_error,
            "threshold": self.threshold,
        }