import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langfuse.decorators import observe

class ContextualizationAgent:
    def __init__(self):
        # Inicializamos el modelo de OpenAI a través de LangChain
        # Usamos GPT-4o por su alta capacidad de razonamiento.
        # Nuevamente, temperatura baja para evitar creatividad innecesaria.
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Diseñamos el System Prompt especializado (El rol del Agente)
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", 
             "Eres un Analista Legal Senior en la empresa LegalMove. "
             "Tu responsabilidad exclusiva es recibir el texto de un contrato original y el texto de su adenda/enmienda, "
             "y producir un análisis de estructura comparada (un mapa contextual). "
             "\n\nInstrucciones estrictas:"
             "\n1. Identifica qué secciones/cláusulas existen en ambos documentos."
             "\n2. Explica cómo se corresponden entre sí (ej. 'La Cláusula 2 de la adenda hace referencia a la Sección 4 del original')."
             "\n3. Describe el propósito general de cada bloque de texto."
             "\n4. IMPORTANTE: NO extraigas ni resumas los cambios específicos aún. Tu salida debe ser un mapa estructurado que sirva de guía para un auditor posterior."
             ),
            ("user", 
             "A continuación te presento los documentos."
             "\n\n--- CONTRATO ORIGINAL ---\n{original_text}"
             "\n\n--- ADENDA / ENMIENDA ---\n{amendment_text}"
             "\n\nPor favor, genera el mapa contextual."
            )
        ])
        
        # Creamos la cadena de LangChain (Prompt + Modelo)
        self.chain = self.prompt_template | self.llm

    @observe(name="contextualization_agent")
    def run(self, original_text: str, amendment_text: str) -> str:
        """
        Ejecuta el agente de contextualización recibiendo los textos parseados.
        """
        print("JARVIS: Agente de Contextualización iniciando mapeo...")
        
        # Ejecutamos la cadena pasándole las variables dinámicas
        response = self.chain.invoke({
            "original_text": original_text,
            "amendment_text": amendment_text
        })
        
        # Retornamos el contenido del mensaje generado
        return response.content
