import os
import time
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langfuse.decorators import observe, langfuse_context
from src.utils.prompt_loader import get_contextualization_prompts


class ContextualizationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        system_prompt, user_prompt = get_contextualization_prompts()
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        
        self.chain = self.prompt_template | self.llm

    @observe(name="contextualization_agent")
    def run(self, original_text: str, amendment_text: str) -> str:
        """
        Analyzes contract structure and creates a contextual mapping.
        
        Args:
            original_text: Text of the original contract
            amendment_text: Text of the amendment/adenda
            
        Returns:
            Contextual mapping analysis
        """
        print("Running contextualization analysis...")
        start_time = time.perf_counter()

        try:
            response = self.chain.invoke({
                "original_text": original_text,
                "amendment_text": amendment_text
            })

            context_map = getattr(response, "content", response)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000)

            langfuse_context.update_current_observation(
                output={
                    "context_map_length": len(context_map or ""),
                    "elapsed_ms": elapsed_ms,
                }
            )

            return context_map

        except Exception as error:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000)
            langfuse_context.update_current_observation(
                level="ERROR",
                status_message=f"Contextualization failed: {error}",
                output={
                    "elapsed_ms": elapsed_ms,
                }
            )
            raise RuntimeError(f"Error en el agente de contextualización: {error}") from error
