from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


IMAGE_SIZE = (128, 128)
CLASSES = ["clean", "blurry", "dark"]


def create_document_image(seed: int) -> Image.Image:
    rng = np.random.default_rng(seed)

    image = Image.new("L", IMAGE_SIZE, color=255)
    draw = ImageDraw.Draw(image)

    for y in range(15, 115, 10):
        width = int(rng.integers(50, 110))
        shade = int(rng.integers(0, 80))
        draw.rectangle(
            (10, y, 10 + width, y + 2),
            fill=shade,
        )

    return image


def generate_dataset(
    output_dir: Path,
    samples_per_class: int = 300,
) -> None:
    for class_name in CLASSES:
        (output_dir / class_name).mkdir(
            parents=True,
            exist_ok=True,
        )

    for index in range(samples_per_class):
        base = create_document_image(index)

        clean = base

        blurry = base.filter(
            ImageFilter.GaussianBlur(radius=3)
        )

        dark = ImageEnhance.Brightness(base).enhance(0.25)

        images = {
            "clean": clean,
            "blurry": blurry,
            "dark": dark,
        }

        for class_name, image in images.items():
            image.save(
                output_dir
                / class_name
                / f"{class_name}_{index}.png"
            )


if __name__ == "__main__":
    dataset_path = (
        Path(__file__).parent / "generated"
    )

    generate_dataset(dataset_path)

    print(f"Dataset generated at: {dataset_path}")