import os
from pathlib import Path

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}


def validate_image_path(image_path: str) -> None:
    """Valida que la imagen exista y tenga un formato soportado."""
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Imagen no encontrada: {image_path}")

    extension = Path(image_path).suffix.lower()
    if extension not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError(
            f"Formato de imagen no soportado: {extension}. Usa JPG, PNG, BMP, TIFF o WEBP."
        )


def validate_image_paths(original_image_path: str, amendment_image_path: str) -> None:
    """Valida dos rutas de imagen y sus extensiones."""
    invalid_paths = []
    invalid_extensions = []

    for path in (original_image_path, amendment_image_path):
        try:
            validate_image_path(path)
        except FileNotFoundError:
            invalid_paths.append(path)
        except ValueError:
            invalid_extensions.append(path)

    if invalid_paths:
        raise FileNotFoundError(f"No se encontraron las siguientes imágenes: {invalid_paths}")

    if invalid_extensions:
        raise ValueError(
            f"Las siguientes imágenes usan un formato no soportado: {invalid_extensions}. "
            "Utiliza JPG, PNG, BMP, TIFF o WEBP."
        )
