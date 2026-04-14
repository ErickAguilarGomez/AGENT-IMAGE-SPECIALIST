from pydantic import BaseModel, Field
from typing import List

class ContractChangeOutput(BaseModel):
    """
    Esquema estricto para validar la salida del Agente 2 (Extracción de cambios).
    """
    sections_changed: List[str] = Field(
        ..., 
        description="Lista de identificadores de las secciones que fueron modificadas (ej. 'Cláusula 3', 'Anexo B')."
    )
    topics_touched: List[str] = Field(
        ..., 
        description="Lista de categorías legales o comerciales afectadas (ej. 'Confidencialidad', 'Monto', 'Jurisdicción')."
    )
    summary_of_the_change: str = Field(
        ..., 
        description="Descripción detallada, precisa y profesional de todos los cambios introducidos por la enmienda o adenda."
    )