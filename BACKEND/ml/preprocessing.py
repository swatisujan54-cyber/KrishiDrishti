"""Image preprocessing for the crop disease model.

The preprocessing pipeline converts a Pillow image into the numpy array the
model expects.  Adjust this module to match your trained model's requirements
(e.g. normalisation mean/std, channel order) when you integrate a real model.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
from PIL import Image

from app.core.config import settings

logger = logging.getLogger("krishidrishti.ml.preprocessing")


def load_labels(labels_path: str | None = None) -> dict[str, str]:
    """Load the label mapping from ``labels.json``.

    Returns a dict ``{index_str: label}`` (the ``_meta`` key is stripped).
    Raises ``FileNotFoundError`` if the file doesn't exist.
    """
    path = Path(labels_path or settings.LABELS_PATH)
    if not path.exists():
        raise FileNotFoundError(f"Labels file not found: {path}")
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    # Remove metadata keys that start with "_"
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def preprocess_image(
    image: Image.Image,
    target_size: tuple[int, int] | None = None,
) -> np.ndarray:
    """Preprocess a Pillow image into a model-ready numpy array.

    Steps:
    1. Convert to RGB.
    2. Resize to *target_size* (defaults to ``settings.image_size_tuple``).
    3. Convert to float32 numpy array in [0, 1] range.

    When integrating a real model, adjust the normalisation below to match
    what the model was trained with (e.g. ImageNet mean/std subtraction).
    """
    size = target_size or settings.image_size_tuple
    img = image.convert("RGB").resize(size, Image.Resampling.LANCZOS)
    arr = np.array(img, dtype=np.float32) / 255.0
    return arr
