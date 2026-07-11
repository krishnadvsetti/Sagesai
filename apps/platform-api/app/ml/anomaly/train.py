from pathlib import Path

import joblib
import numpy as np
import torch
from sklearn.metrics import (
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch import nn

from app.ml.anomaly.data.generate import (
    FEATURES,
    generate_authentication_data,
)
from app.ml.anomaly.models.autoencoder import AnomalyAutoencoder


ARTIFACT_DIR = Path(__file__).parent / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "autoencoder.pt"
SCALER_PATH = ARTIFACT_DIR / "scaler.joblib"
THRESHOLD_PATH = ARTIFACT_DIR / "threshold.npy"


def train() -> None:
    torch.manual_seed(42)
    np.random.seed(42)

    dataframe = generate_authentication_data(
        samples=5000,
        random_state=42,
    )

    train_df, test_df = train_test_split(
        dataframe,
        test_size=0.2,
        random_state=42,
        stratify=dataframe["label"],
    )

    # Autoencoder learns normal behaviour only.
    normal_train = train_df[train_df["label"] == 0]

    scaler = StandardScaler()
    scaler.fit(normal_train[FEATURES])

    x_train = scaler.transform(normal_train[FEATURES])
    x_test = scaler.transform(test_df[FEATURES])
    y_test = test_df["label"].to_numpy()

    train_tensor = torch.tensor(
        x_train,
        dtype=torch.float32,
    )

    test_tensor = torch.tensor(
        x_test,
        dtype=torch.float32,
    )

    model = AnomalyAutoencoder(
        input_dim=len(FEATURES),
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=0.001,
    )

    loss_function = nn.MSELoss()

    model.train()

    epochs = 50

    for epoch in range(epochs):
        optimizer.zero_grad()

        reconstructed = model(train_tensor)
        loss = loss_function(
            reconstructed,
            train_tensor,
        )

        loss.backward()
        optimizer.step()

        if (epoch + 1) % 10 == 0:
            print(
                f"Epoch {epoch + 1}/{epochs} "
                f"- Loss: {loss.item():.6f}"
            )

    model.eval()

    with torch.no_grad():
        train_reconstruction = model(train_tensor)

        train_errors = torch.mean(
            (train_tensor - train_reconstruction) ** 2,
            dim=1,
        ).numpy()

        test_reconstruction = model(test_tensor)

        test_errors = torch.mean(
            (test_tensor - test_reconstruction) ** 2,
            dim=1,
        ).numpy()

    # 99th percentile of normal training reconstruction error.
    threshold = float(
        np.percentile(train_errors, 99)
    )

    predictions = (
        test_errors > threshold
    ).astype(int)

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0,
    )
    recall = recall_score(
        y_test,
        predictions,
        zero_division=0,
    )
    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0,
    )
    roc_auc = roc_auc_score(
        y_test,
        test_errors,
    )

    print(f"\nThreshold: {threshold:.6f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"ROC-AUC: {roc_auc:.4f}")

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0,
        )
    )

    ARTIFACT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    torch.save(
        model.state_dict(),
        MODEL_PATH,
    )

    joblib.dump(
        scaler,
        SCALER_PATH,
    )

    np.save(
        THRESHOLD_PATH,
        np.array([threshold]),
    )

    print("\nArtifacts saved:")
    print(MODEL_PATH)
    print(SCALER_PATH)
    print(THRESHOLD_PATH)


if __name__ == "__main__":
    train()