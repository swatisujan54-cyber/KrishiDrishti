"""Prediction service — interface, factory, and model integration.

The service is loaded **once** when the application starts (see the
``get_prediction_service`` singleton).  When ``MODEL_PATH`` is empty the mock
implementation is used; when a real model path is configured the
``KerasPredictionService`` is used (requires TensorFlow to be installed).

To replace the mock with a real model:
1. Train a crop-disease classification model and save it as a ``.h5`` or
   ``SavedModel`` directory.
2. Set ``MODEL_PATH`` in ``.env`` to the model file/directory path.
3. Replace ``ml/labels.json`` with your model's label mapping.
4. Adjust ``ml/preprocessing.py`` if your model needs different preprocessing.
5. Install TensorFlow (``pip install tensorflow``) — it is not in the default
   requirements to keep the project lightweight.
"""

from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np
from PIL import Image

from app.core.config import settings
from app.models.scan import PredictionStatus
from app.schemas.prediction import PredictionCandidate, PredictionResult

logger = logging.getLogger("krishidrishti.prediction")


class PredictionService(ABC):
    """Abstract interface for crop disease prediction."""

    @property
    @abstractmethod
    def is_mock(self) -> bool:
        """``True`` if this is a mock (not a real model)."""
        ...

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Version identifier of the loaded model."""
        ...

    @abstractmethod
    def predict(self, image: Image.Image) -> PredictionResult:
        """Run inference on *image* and return a structured prediction."""
        ...


# --------------------------------------------------------------------------- #
# Mock prediction service                                                      #
# --------------------------------------------------------------------------- #

class MockPredictionService(PredictionService):
    """A clearly-labeled mock that produces deterministic demo predictions.

    This is NOT a real AI model.  Predictions are generated from simple image
    statistics (average colour, brightness) so that results are stable and
    testable.  Never present mock results as genuine diagnoses.
    """

    def __init__(self, labels: dict[str, str]):
        self._labels = labels
        self._version = "mock-0.0.1"

    @property
    def is_mock(self) -> bool:
        return True

    @property
    def model_version(self) -> str:
        return self._version

    def predict(self, image: Image.Image) -> PredictionResult:
        """Produce a deterministic mock prediction from image statistics."""
        try:
            img = image.convert("RGB").resize((64, 64))
            arr = np.array(img, dtype=np.float32)
            # Average colour channels
            mean_rgb = arr.mean(axis=(0, 1))  # (3,)
            # Brightness = average of all channels
            brightness = float(mean_rgb.mean())
            # Colour variance — higher = more complex image = "higher confidence"
            std = float(arr.std())

            # Deterministically pick a label index from image statistics.
            # This makes the same image always return the same prediction.
            seed = int(mean_rgb[0] * 1000 + mean_rgb[1] * 100 + mean_rgb[2] * 10)
            label_indices = sorted(self._labels.keys(), key=lambda k: int(k))
            if not label_indices:
                return PredictionResult(
                    status=PredictionStatus.failed,
                    model_version=self._version,
                    is_mock=True,
                    error_message="No labels configured.",
                )
            chosen_idx = label_indices[seed % len(label_indices)]
            chosen_label = self._labels[chosen_idx]

            # Confidence: maps std from [0, ~80] to [0.45, 0.95].
            # A very uniform image (low std) gets low confidence → uncertain.
            confidence = min(0.95, max(0.40, 0.45 + std / 160.0))

            # Build top-k predictions with decreasing confidence.
            top_k = min(settings.PREDICTION_TOP_K, len(label_indices))
            candidates: list[PredictionCandidate] = []
            remaining = [i for i in label_indices if i != chosen_idx]
            for i in range(top_k):
                if i == 0:
                    candidates.append(PredictionCandidate(label=chosen_label, confidence=round(confidence, 4)))
                else:
                    if remaining:
                        idx = remaining.pop(0)
                        c = round(confidence * (0.7 ** i), 4)
                        candidates.append(PredictionCandidate(label=self._labels[idx], confidence=c))

            # Determine status based on confidence threshold.
            if confidence < settings.PREDICTION_CONFIDENCE_THRESHOLD:
                status_ = PredictionStatus.uncertain
            else:
                status_ = PredictionStatus.completed

            logger.info("Mock prediction: label=%s confidence=%.4f status=%s",
                        chosen_label, confidence, status_.value)
            return PredictionResult(
                label=chosen_label,
                confidence=round(confidence, 4),
                top_predictions=candidates,
                status=status_,
                model_version=self._version,
                is_mock=True,
            )
        except Exception as e:
            logger.exception("Mock prediction failed: %s", e)
            return PredictionResult(
                status=PredictionStatus.failed,
                model_version=self._version,
                is_mock=True,
                error_message=str(e),
            )


# --------------------------------------------------------------------------- #
# Real (Keras/TF) prediction service                                           #
# --------------------------------------------------------------------------- #

class KerasPredictionService(PredictionService):
    """Loads a TensorFlow/Keras model and runs real inference.

    Requires ``tensorflow`` to be installed.  The model is loaded once on
    instantiation; ``predict`` runs a single forward pass.

    Note: This class is only used when ``MODEL_PATH`` is set in the
    environment.  It is intentionally kept minimal — adjust preprocessing and
    post-processing to match your specific model.
    """

    def __init__(self, model_path: str, labels: dict[str, str]):
        import tensorflow as tf  # noqa: imported lazily
        self._tf = tf
        self._labels = labels
        self._version = "keras-1.0.0"
        if Path(model_path).is_dir():
            self._model = tf.keras.models.load_model(model_path)
        else:
            self._model = tf.keras.models.load_model(model_path)
        logger.info("Loaded Keras model from %s", model_path)

    @property
    def is_mock(self) -> bool:
        return False

    @property
    def model_version(self) -> str:
        return self._version

    def predict(self, image: Image.Image) -> PredictionResult:
        from ml.preprocessing import preprocess_image

        try:
            arr = preprocess_image(image)
            # Add batch dimension
            batch = np.expand_dims(arr, axis=0)
            preds = self._model.predict(batch, verbose=0)[0]  # type: ignore[attr-defined]

            # Get top-k predictions
            top_k = min(settings.PREDICTION_TOP_K, len(self._labels))
            top_indices = np.argsort(preds)[::-1][:top_k]

            candidates = []
            label_indices = sorted(self._labels.keys(), key=lambda k: int(k))
            for rank, idx in enumerate(top_indices):
                key = label_indices[idx]
                candidates.append(PredictionCandidate(
                    label=self._labels[key],
                    confidence=round(float(preds[idx]), 4),
                ))

            top_label = candidates[0].label if candidates else None
            top_conf = candidates[0].confidence if candidates else None

            if top_conf is None or top_conf < settings.PREDICTION_CONFIDENCE_THRESHOLD:
                status_ = PredictionStatus.uncertain
            else:
                status_ = PredictionStatus.completed

            return PredictionResult(
                label=top_label,
                confidence=top_conf,
                top_predictions=candidates,
                status=status_,
                model_version=self._version,
                is_mock=False,
            )
        except Exception as e:
            logger.exception("Keras prediction failed: %s", e)
            return PredictionResult(
                status=PredictionStatus.failed,
                model_version=self._version,
                is_mock=False,
                error_message=str(e),
            )


# --------------------------------------------------------------------------- #
# Factory / singleton                                                         #
# --------------------------------------------------------------------------- #

_service: PredictionService | None = None


def _load_labels() -> dict[str, str]:
    """Load labels from the configured labels file."""
    path = Path(settings.LABELS_PATH)
    if not path.exists():
        logger.warning("Labels file %s not found; using empty labels.", path)
        return {}
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v for k, v in raw.items() if not k.startswith("_")}


def get_prediction_service() -> PredictionService:
    """Return the singleton prediction service (mock or real).

    Loads the model once and caches it for the lifetime of the process.
    """
    global _service
    if _service is not None:
        return _service

    labels = _load_labels()

    if settings.MODEL_PATH:
        try:
            _service = KerasPredictionService(settings.MODEL_PATH, labels)
            logger.info("Real model loaded: %s", settings.MODEL_PATH)
        except ImportError:
            logger.warning(
                "TensorFlow not installed. Falling back to mock. "
                "Install with: pip install tensorflow"
            )
            _service = MockPredictionService(labels)
        except Exception:
            logger.exception("Failed to load model; falling back to mock.")
            _service = MockPredictionService(labels)
    else:
        _service = MockPredictionService(labels)
        logger.info("Using mock prediction service (no MODEL_PATH configured).")

    return _service


def reset_prediction_service() -> None:
    """Reset the singleton (used in tests to switch services)."""
    global _service
    _service = None
