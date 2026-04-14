import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langfuse.decorators import observe
from src.models import ContractChangeOutput

class ExtractionAgent:
    def __init__(self):
        # Inicializamos GPT-4o con temperatura 0. ¡Cero tolerancia a la invención!
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # AQUÍ OCURRE LA MAGIA: 
        # Obligamos al LLM a que su salida sea validada estrictamente por nuestro modelo Pydantic
        self.structured_llm = self.llm.with_structured_output(ContractChangeOutput)
        
        # Diseñamos el System Prompt especializado para el Auditor
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", 
             "Eres un Auditor Legal de élite en la empresa LegalMove. "
             "Tu responsabilidad exclusiva es identificar, aislar y describir cada cambio "
             "introducido por la enmienda (adenda) respecto al contrato original. "
             "\n\nReglas estrictas:"
             "\n1. Distingue claramente entre adiciones, eliminaciones y modificaciones."
             "\n2. Apóyate en el 'Mapa Contextual' proporcionado por el Analista Senior para orientarte."
             "\n3. Tu salida debe cumplir estrictamente con el esquema JSON solicitado."
             ),
            ("user", 
             "Aquí tienes la información procesada:"
             "\n\n--- MAPA CONTEXTUAL (Del Analista) ---\n{context_map}"
             "\n\n--- CONTRATO ORIGINAL ---\n{original_text}"
             "\n\n--- ADENDA / ENMIENDA ---\n{amendment_text}"
             "\n\nExtrae las diferencias y devuelve los datos en el formato estructurado requerido."
            )
        ])
        
        # Conectamos el prompt con el LLM ESTRUCTURADO
        self.chain = self.prompt_template | self.structured_llm

    @observe(name="extraction_agent")
    def run(self, context_map: str, original_text: str, amendment_text: str) -> ContractChangeOutput:
        """
        Ejecuta el agente de extracción y devuelve un objeto validado por Pydantic.
        """
        print("JARVIS: Agente de Extracción iniciando auditoría profunda...")
        
        # Ejecutamos la cadena. La respuesta ya no será un simple string,
        # será un objeto ContractChangeOutput validado y perfecto.
        response = self.chain.invoke({
            "context_map": context_map,
            "original_text": original_text,
            "amendment_text": amendment_text
        })
        
        return response