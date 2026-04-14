import base64
import os
from openai import OpenAI
from dotenv import load_dotenv
from langfuse.decorators import observe

# 1. Encendemos el reactor y cargamos nuestras claves secretas
load_dotenv()

# 2. Inicializamos el cliente de OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path: str) -> str:
    """Codifica una imagen local a formato base64 para enviarla a la API."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# El decorador @observe conecta esta función a nuestro panel de telemetría de Langfuse
@observe(name="parse_contract_image")
def parse_contract_image(image_path: str) -> str:
    """
    Toma la ruta de una imagen, la convierte a base64 y usa GPT-4o (Vision)
    para extraer todo el texto del documento de forma fiel.
    """
    print(f"JARVIS: Escaneando imagen {image_path}...")
    
    # Paso A: Codificar la imagen
    base64_image = encode_image(image_path)
    
    # Paso B: Construir nuestro System Prompt (Las instrucciones estrictas)
    prompt = (
        "Eres un experto analista legal y un sistema OCR de altísima precisión. "
        "Tu única tarea es extraer TODO el texto de la imagen proporcionada de la forma más fiel posible. "
        "Mantén la estructura jerárquica original, cláusulas, párrafos y viñetas. "
        "NO inventes información, NO resumas, NO analices. Solo devuelve el texto transcrito."
    )

    # Paso C: Llamar a la API de OpenAI
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
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_tokens=3000,
        temperature=0.0 # MUY IMPORTANTE
    )
    
    # Devolvemos el texto puro
    return response.choices[0].message.content