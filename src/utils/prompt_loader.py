import os
from pathlib import Path
from typing import Tuple


def load_prompt(prompt_name: str) -> str:
    """
    Carga un prompt desde los archivos txt en la carpeta prompts.
    
    Args:
        prompt_name: Nombre del archivo sin extensión (ej: 'ocr_extraction')
        
    Returns:
        Contenido del archivo de prompt
        
    Raises:
        FileNotFoundError: Si el archivo de prompt no existe
    """
    prompts_dir = Path(__file__).parent.parent / "prompts"
    prompt_file = prompts_dir / f"{prompt_name}.txt"
    
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_file}")
    
    with open(prompt_file, "r", encoding="utf-8") as file:
        return file.read()


def load_prompt_parts(prompt_name: str) -> Tuple[str, str]:
    """
    Carga un prompt y lo divide en partes SYSTEM y USER.
    
    Args:
        prompt_name: Nombre del archivo sin extensión
        
    Returns:
        Tupla (system_prompt, user_prompt)
    """
    content = load_prompt(prompt_name)
    parts = content.split("USER:")
    
    system = parts[0].replace("SYSTEM:", "").strip()
    user = parts[1].strip() if len(parts) > 1 else ""
    
    return system, user


def get_ocr_prompt() -> str:
    """Obtiene el prompt para extracción OCR de contratos."""
    return load_prompt("ocr_extraction")


def get_contextualization_prompts() -> Tuple[str, str]:
    """Obtiene los prompts para análisis de contextualización."""
    return load_prompt_parts("contextualization_analysis")


def get_extraction_audit_prompts() -> Tuple[str, str]:
    """Obtiene los prompts para auditoría de extracción de cambios."""
    return load_prompt_parts("extraction_audit")
