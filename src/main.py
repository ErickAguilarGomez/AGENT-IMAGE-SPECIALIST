import sys
import json
from dotenv import load_dotenv
from langfuse.decorators import observe, langfuse_context

# Importamos nuestros módulos recién ensamblados
from src.image_parser import parse_contract_image
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent

# Cargamos el reactor (variables de entorno)
load_dotenv()

@observe(name="contract-analysis") # Este es el SPAN RAÍZ que pide la rúbrica
def main(original_image_path: str, amendment_image_path: str):
    """
    Función principal que orquesta el pipeline completo de análisis de contratos.
    """
    print("\n" + "="*50)
    print("🤖 INICIANDO PROTOCOLO LEGALMOVE (By Tony Stark)")
    print("="*50 + "\n")

    try:
        # ETAPA 1: Parsing Multimodal de Imágenes
        print("[1/4] Extrayendo texto de la imagen ORIGINAL...")
        original_text = parse_contract_image(original_image_path)
        
        print("[2/4] Extrayendo texto de la imagen de la ADENDA...")
        amendment_text = parse_contract_image(amendment_image_path)

        # ETAPA 2: Agente 1 - Contextualización
        print("[3/4] Despertando al Agente Analista Senior (Mapeo Contextual)...")
        agent1 = ContextualizationAgent()
        context_map = agent1.run(
            original_text=original_text, 
            amendment_text=amendment_text
        )

        # ETAPA 3: Agente 2 - Extracción de Cambios (Validado por Pydantic)
        print("[4/4] Despertando al Agente Auditor (Extracción Estricta)...")
        agent2 = ExtractionAgent()
        final_result = agent2.run(
            context_map=context_map,
            original_text=original_text,
            amendment_text=amendment_text
        )

        # Mostramos los resultados finales formateados como un JSON perfecto
        print("\n" + "="*50)
        print("✅ ANÁLISIS COMPLETADO EXITOSAMENTE")
        print("="*50)
        
        # model_dump_json() es una función nativa de Pydantic que convierte el objeto a JSON
        print(final_result.model_dump_json(indent=4))
        
        # Añadimos el resultado al rastro de Langfuse para la auditoría
        langfuse_context.update_current_observation(
            output=final_result.model_dump()
        )

    except Exception as e:
        print("\n❌ ALERTA ROJA: Ocurrió un error en el sistema.")
        print(f"Detalle técnico: {str(e)}")
        langfuse_context.update_current_observation(level="ERROR", status_message=str(e))

if __name__ == "__main__":
    # El entry point que acepta dos paths de imágenes como argumentos de terminal
    if len(sys.argv) != 3:
        print("Uso correcto del sistema: python -m src.main <path_imagen_original> <path_imagen_adenda>")
        sys.exit(1)
    
    path_original = sys.argv[1]
    path_adenda = sys.argv[2]
    
    main(path_original, path_adenda)
    
    # Aseguramos que todos los logs se envíen a Langfuse antes de cerrar el programa
    langfuse_context.flush()