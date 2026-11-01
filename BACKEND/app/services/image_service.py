"""Image upload validation and safe storage.

Uses Pillow to validate that the uploaded bytes are a real, non-corrupt image
in an allowed format.  Filenames are generated (UUID) — never trusted from
the client — to prevent path-traversal and filename collisions.
"""

from __future__ import annotations

import logging
import os
import uuid

from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.core.exceptions import AppError

logger = logging.getLogger("krishidrishti.image")

# Extension mapping for Pillow format names.
_FORMAT_EXTENSIONS = {
    "JPEG": ".jpg",
    "PNG": ".png",
    "WEBP": ".webp",
}


def validate_image(file_bytes: bytes) -> Image.Image:
    """Validate raw upload bytes and return a Pillow ``Image``.

    Checks (in order):
    1. File is not empty.
    2. File size is within the configured limit.
    3. Pillow can open and fully load it (catches corrupt / truncated files).
    4. Format is in the allowed list.

    Raises ``AppError`` (400) for any validation failure.
    """
    if not file_bytes:
        raise AppError("The uploaded file is empty.", error_code="empty_file")

    if len(file_bytes) > settings.MAX_IMAGE_SIZE_BYTES:
        max_mb = settings.MAX_IMAGE_SIZE_BYTES / (1024 * 1024)
        raise AppError(
            f"File is too large. Maximum allowed size is {max_mb:.1f} MB.",
            error_code="file_too_large",
        )

    try:
        img = Image.open(_BytesIO(file_bytes))
        img.load()  # force full decode — catches truncated images
    except UnidentifiedImageError:
        raise AppError(
            "The file is not a valid image or is corrupt.",
            error_code="invalid_image",
        )
    except Exception:
        raise AppError(
            "Could not read the image file. It may be corrupt or in an unsupported format.",
            error_code="invalid_image",
        )

    fmt = (img.format or "").upper()
    if fmt not in settings.allowed_image_formats_list:
        allowed = ", ".join(settings.allowed_image_formats_list)
        raise AppError(
            f"Unsupported image format '{fmt}'. Allowed: {allowed}.",
            error_code="unsupported_format",
        )

    return img


def _BytesIO(data: bytes):
    """Local import to keep the top-level clean."""
    from io import BytesIO
    return BytesIO(data)


def save_upload(img: Image.Image, *, sub_dir: str = "") -> str:
    """Save *img* to the upload directory with a generated filename.

    Returns the relative path (from UPLOAD_DIR) that can be stored in the DB.
    """
    fmt = (img.format or "JPEG").upper()
    ext = _FORMAT_EXTENSIONS.get(fmt, ".jpg")
    filename = f"{uuid.uuid4().hex}{ext}"

    target_dir = os.path.join(settings.UPLOAD_DIR, sub_dir) if sub_dir else settings.UPLOAD_DIR
    os.makedirs(target_dir, exist_ok=True)

    full_path = os.path.join(target_dir, filename)
    # Re-encode to strip any embedded malicious metadata.
    save_format = "JPEG" if fmt in ("JPEG", "JPG") else fmt
    if save_format == "JPEG":
        img.convert("RGB").save(full_path, format=save_format, quality=90)
    else:
        img.save(full_path, format=save_format)

    relative = os.path.relpath(full_path, settings.UPLOAD_DIR)
    logger.info("Saved uploaded image to %s", relative)
    return relative


def delete_upload(relative_path: str) -> None:
    """Delete an uploaded image file by its relative path.

    Safely ignores missing files.  Validates the path stays within UPLOAD_DIR.
    """
    if not relative_path:
        return
    full_path = os.path.normpath(os.path.join(settings.UPLOAD_DIR, relative_path))
    # Prevent path traversal — ensure the resolved path is inside UPLOAD_DIR.
    upload_abs = os.path.abspath(settings.UPLOAD_DIR)
    if not os.path.abspath(full_path).startswith(upload_abs):
        logger.warning("Refused to delete file outside upload dir: %s", relative_path)
        return
    try:
        os.remove(full_path)
        logger.info("Deleted uploaded image %s", relative_path)
    except FileNotFoundError:
        pass
    except OSError as e:
        logger.warning("Could not delete %s: %s", relative_path, e)


def load_image_for_prediction(relative_path: str) -> Image.Image:
    """Load a previously-saved image for model inference."""
    full_path = os.path.join(settings.UPLOAD_DIR, relative_path)
    return Image.open(full_path)
