# IMAGE_ANALIZER

## Descripción

`IMAGE_ANALIZER` es un pipeline de análisis de contratos que orquesta un modelo multimodal GPT-4o Vision para extraer texto de imágenes de contratos y adendas, y dos agentes especializados para generar un mapa contextual y un resumen estructurado de cambios.

## Arquitectura

1. `src/image_parser.py`
   - `parse_contract_image()` usa GPT-4o Vision con imagen codificada en base64.
   - Extrae texto del contrato manteniendo la estructura jerárquica y las cláusulas.

2. `src/agents/contextualization_agent.py`
   - `ContextualizationAgent` genera un mapa contextual comparando contrato original y adenda.
   - Su responsabilidad es definir correspondencias entre secciones/cláusulas sin extraer cambios.

3. `src/agents/extraction_agent.py`
   - `ExtractionAgent` recibe el mapa contextual y los textos originales.
   - El resultado es validado estrictamente con el modelo Pydantic `ContractChangeOutput`.

4. `src/main.py`
   - Orquesta el pipeline completo.
   - Valida rutas de entrada.
   - Registra observabilidad con Langfuse en cada etapa.

## Por qué esta arquitectura cumple la rúbrica?

- Multimodalidad Vision: usa GPT-4o Vision y datos base64 para extraer texto de imágenes.
- Dos agentes especializados: `ContextualizationAgent` y `ExtractionAgent` tienen responsabilidades separadas y un handoff lógico.
- Validación estricta con Pydantic: `ContractChangeOutput` asegura la salida JSON final.
- Observabilidad: hay spans Langfuse y metadatos de cada etapa para auditoría.

## Instrucciones de instalación

1. Activa tu entorno virtual:

```powershell
& .\venv\Scripts\Activate.ps1
```

2. Instala dependencias:

```powershell
pip install -r requirements.txt
```

3. Crea un archivo `.env` con tu clave de OpenAI:

```powershell
copy .env.example .env
```

4. Completa el valor en `.env`:

```text
OPENAI_API_KEY=tu_api_key_aqui
```

## Ejecución

```powershell
python -m src.main data/test_contracts/original_simple.png data/test_contracts/adenda_simple.png
```

## Validación de salida

El resultado final se imprime en JSON y se valida con Pydantic. El objeto final contiene:

- `sections_changed`
- `topics_touched`
- `summary_of_the_change`

## Buenas prácticas implementadas

- Validación de rutas y formatos de imagen antes de iniciar el pipeline.
- Manejo de errores con mensajes claros y logs de Langfuse.
- Separación modular de responsabilidades.
- Documentación en `README.md` y ejemplo de `.env`.

## Estructura del repositorio

- `src/`
  - `image_parser.py`
  - `main.py`
  - `models.py`
  - `agents/`
    - `contextualization_agent.py`
    - `extraction_agent.py`
  - `utils/prompt_loader.py`
  - `prompts/`
    - `ocr_extraction.txt`
    - `contextualization_analysis.txt`
    - `extraction_audit.txt`
- `requirements.txt`
- `.env.example`
- `data/test_contracts/`

## Nota

Para la defensa, ten a mano el flujo de datos: OCR -> Mapa contextual -> Auditoría estructurada. Explica cómo cada etapa agrega trazabilidad y cómo Langfuse captura el workflow en vivo.
