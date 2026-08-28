import logging

from ollama import Client

from src.interfaces.i_llm_client import ILLMClient
from src.models.prompt_config import PromptConfig

logger = logging.getLogger(__name__)


class OllamaClient(ILLMClient):
    """An LLM client strictly responsible for API communication."""

    def __init__(
        self,
        prompt_config: PromptConfig,
        host: str,
        model_name: str,
    ) -> None:
        self.client = Client(host=host)
        self.model_name = model_name
        self.prompt_config = prompt_config

        logger.debug(f"Initialized OllamaClient with model '{self.model_name}' on host '{host}'")

    def generate_message(self, contact_name: str) -> str:
        user_prompt = self.prompt_config.user_prompt_template.format(contact_name=contact_name)

        logger.info(f"Generating message for contact: {contact_name}")

        response = self.client.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.prompt_config.system_instruction},
                {"role": "user", "content": user_prompt},
            ],
        )

        logger.debug(f"Successfully received LLM response for {contact_name}")

        return str(response["message"]["content"])
