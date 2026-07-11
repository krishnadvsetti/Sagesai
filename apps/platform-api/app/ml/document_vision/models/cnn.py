import tensorflow as tf


def build_document_quality_cnn(
    num_classes: int = 3,
) -> tf.keras.Model:
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(
                shape=(128, 128, 1)
            ),
            tf.keras.layers.Rescaling(1.0 / 255),
            tf.keras.layers.Conv2D(
                16,
                3,
                activation="relu",
            ),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(
                32,
                3,
                activation="relu",
            ),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.Conv2D(
                64,
                3,
                activation="relu",
            ),
            tf.keras.layers.MaxPooling2D(),
            tf.keras.layers.GlobalAveragePooling2D(),
            tf.keras.layers.Dense(
                64,
                activation="relu",
            ),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(
                num_classes,
                activation="softmax",
            ),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model