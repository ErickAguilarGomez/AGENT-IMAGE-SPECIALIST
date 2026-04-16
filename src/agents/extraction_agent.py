import os
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langfuse.decorators import observe, langfuse_context
from src.models import ContractChangeOutput
from src.utils.prompt_loader import get_extraction_audit_prompts


class ExtractionAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.structured_llm = self.llm.with_structured_output(ContractChangeOutput)
        
        system_prompt, user_prompt = get_extraction_audit_prompts()
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        
        self.chain = self.prompt_template | self.structured_llm

    @observe(name="extraction_agent")
    def run(self, context_map: str, original_text: str, amendment_text: str) -> ContractChangeOutput:
        """
        Extracts and validates changes between contract and amendment.
        
        Args:
            context_map: Contextual mapping from the contextualization agent
            original_text: Text of the original contract
            amendment_text: Text of the amendment/adenda
            
        Returns:
            Structured ContractChangeOutput object with validated changes
        """
        print("Running extraction audit...")
        start_time = time.perf_counter()

        try:
            response = self.chain.invoke({
                "context_map": context_map,
                "original_text": original_text,
                "amendment_text": amendment_text
            })

            if isinstance(response, ContractChangeOutput):
                validated_output = response
            else:
                validated_output = ContractChangeOutput.model_validate(response)

            elapsed_ms = round((time.perf_counter() - start_time) * 1000)
            langfuse_context.update_current_observation(
                output={
                    "sections_changed": validated_output.sections_changed,
                    "topics_touched": validated_output.topics_touched,
                    "summary_length": len(validated_output.summary_of_the_change),
                    "elapsed_ms": elapsed_ms,
                }
            )

            return validated_output

        except Exception as error:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000)
            langfuse_context.update_current_observation(
                level="ERROR",
                status_message=f"Extraction audit failed: {error}",
                output={
                    "elapsed_ms": elapsed_ms,
                }
            )
            raise RuntimeError(f"Error en el agente de extracción: {error}") from error
