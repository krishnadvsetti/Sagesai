from pathlib import Path

import tensorflow as tf

from app.ml.document_vision.models.cnn import (
    build_document_quality_cnn,
)


BASE_DIR = Path(__file__).parent
DATASET_DIR = BASE_DIR / "data" / "generated"
ARTIFACT_DIR = BASE_DIR / "artifacts"
MODEL_PATH = ARTIFACT_DIR / "document_quality.keras"

IMAGE_SIZE = (128, 128)
BATCH_SIZE = 32
SEED = 42


def train() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    train_dataset = tf.keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=0.2,
        subset="training",
        seed=SEED,
        image_size=IMAGE_SIZE,
        color_mode="grayscale",
        batch_size=BATCH_SIZE,
    )

    validation_dataset = tf.keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=0.2,
        subset="validation",
        seed=SEED,
        image_size=IMAGE_SIZE,
        color_mode="grayscale",
        batch_size=BATCH_SIZE,
    )

    class_names = train_dataset.class_names
    print("Classes:", class_names)

    train_dataset = train_dataset.prefetch(
        tf.data.AUTOTUNE
    )
    validation_dataset = validation_dataset.prefetch(
        tf.data.AUTOTUNE
    )

    model = build_document_quality_cnn(
        num_classes=len(class_names)
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
        )
    ]

    model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=10,
        callbacks=callbacks,
    )

    loss, accuracy = model.evaluate(
        validation_dataset,
        verbose=0,
    )

    print(f"\nValidation Loss: {loss:.4f}")
    print(f"Validation Accuracy: {accuracy:.4f}")

    model.save(MODEL_PATH)

    (ARTIFACT_DIR / "classes.txt").write_text(
        "\n".join(class_names),
        encoding="utf-8",
    )

    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    train()