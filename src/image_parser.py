import base64
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from langfuse.decorators import observe, langfuse_context
from src.utils.prompt_loader import get_ocr_prompt

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SUPPORTED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "bmp", "tiff", "webp"}


def validate_image_path(image_path: str) -> str:
    """Validate that the image exists and has a supported file extension."""
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Imagen no encontrada: {image_path}")

    extension = os.path.splitext(image_path)[1].lower().lstrip('.')
    if extension not in SUPPORTED_IMAGE_EXTENSIONS:
        raise ValueError(
            f"Formato de imagen no soportado: {extension}. Usa JPG, PNG, BMP, TIFF o WEBP."
        )
    return extension


def encode_image(image_path: str) -> str:
    """Encodes a local image to base64 format for API transmission."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def build_data_url(image_path: str) -> str:
    """Builds a data URL with the correct MIME type for the image."""
    extension = validate_image_path(image_path)
    mime_type = "jpeg" if extension in {"jpg", "jpeg"} else extension
    return f"data:image/{mime_type};base64,{encode_image(image_path)}"


@observe(name="parse_contract_image")
def parse_contract_image(image_path: str) -> str:
    """
    Extracts text from a contract image using GPT-4o Vision API.

    Args:
        image_path: Path to the contract image file

    Returns:
        Extracted text from the image
    """
    print(f"Processing image: {image_path}")
    start_time = time.perf_counter()

    data_url = build_data_url(image_path)
    prompt = get_ocr_prompt()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=3000,
            temperature=0.0
        )

        extracted_text = response.choices[0].message.content
        elapsed_ms = round((time.perf_counter() - start_time) * 1000)

        langfuse_context.update_current_observation(
            output={
                "image_path": image_path,
                "text_length": len(extracted_text or ""),
                "elapsed_ms": elapsed_ms,
            }
        )

        return extracted_text

    except Exception as error:
        elapsed_ms = round((time.perf_counter() - start_time) * 1000)
        langfuse_context.update_current_observation(
            level="ERROR",
            status_message=f"OCR extraction failed: {error}",
            output={
                "image_path": image_path,
                "elapsed_ms": elapsed_ms,
            }
        )
        raise RuntimeError(f"Error en OCR de imagen: {error}") from error