import sys
from pathlib import Path
from dotenv import load_dotenv
from langfuse.decorators import observe, langfuse_context

from src.image_parser import parse_contract_image
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent

load_dotenv()


def validate_image_paths(original_image_path: str, amendment_image_path: str) -> None:
    """Valida que ambos archivos existan y sean imágenes compatibles."""
    invalid_paths = [path for path in (original_image_path, amendment_image_path) if not Path(path).is_file()]
    if invalid_paths:
        raise FileNotFoundError(f"No se encontraron las siguientes imágenes: {invalid_paths}")

    allowed_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}
    invalid_extensions = [path for path in (original_image_path, amendment_image_path)
                          if Path(path).suffix.lower() not in allowed_extensions]
    if invalid_extensions:
        raise ValueError(
            f"Las siguientes imágenes usan un formato no soportado: {invalid_extensions}. "
            "Utiliza JPG, PNG, BMP, TIFF o WEBP."
        )


@observe(name="contract-analysis")
def main(original_image_path: str, amendment_image_path: str):
    """
    Orchestrates the complete contract analysis pipeline.
    
    Args:
        original_image_path: Path to the original contract image
        amendment_image_path: Path to the amendment/adenda image
    """
    print("\n" + "="*50)
    print("Contract Analysis Pipeline")
    print("="*50 + "\n")

    try:
        validate_image_paths(original_image_path, amendment_image_path)
        langfuse_context.update_current_observation(
            output={
                "original_image_path": original_image_path,
                "amendment_image_path": amendment_image_path,
            }
        )

        print("[1/4] Extracting original contract text...")
        original_text = parse_contract_image(original_image_path)
        
        print("[2/4] Extracting amendment text...")
        amendment_text = parse_contract_image(amendment_image_path)

        print("[3/4] Running contextualization analysis...")
        agent1 = ContextualizationAgent()
        context_map = agent1.run(
            original_text=original_text, 
            amendment_text=amendment_text
        )

        print("[4/4] Running extraction audit...")
        agent2 = ExtractionAgent()
        final_result = agent2.run(
            context_map=context_map,
            original_text=original_text,
            amendment_text=amendment_text
        )

        print("\n" + "="*50)
        print("Analysis completed successfully")
        print("="*50)
        
        print(final_result.model_dump_json(indent=4))
        
        langfuse_context.update_current_observation(
            output={
                "sections_changed": final_result.sections_changed,
                "topics_touched": final_result.topics_touched,
                "summary_length": len(final_result.summary_of_the_change),
                "final_payload": final_result.model_dump(),
            }
        )

    except Exception as e:
        print(f"\nError: {str(e)}")
        langfuse_context.update_current_observation(level="ERROR", status_message=str(e))
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python -m src.main <original_image_path> <amendment_image_path>")
        sys.exit(1)
    
    path_original = sys.argv[1]
    path_adenda = sys.argv[2]
    
    main(path_original, path_adenda)
    langfuse_context.flush()