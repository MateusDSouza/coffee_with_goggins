from ollama import Client

from src.interfaces.i_llm_client import ILLMClient
from src.models.prompt_config import PromptConfig


class OllamaClient(ILLMClient):
    """An LLM client strictly responsible for API communication."""

    def __init__(
        self, prompt_config: PromptConfig, host: str = "http://localhost:11434", model_name: str = "dolphin-llama3"
    ) -> None:
        self.client = Client(host=host)
        self.model_name = model_name
        self.prompt_config = prompt_config

    def generate_message(self, contact_name: str) -> str:
        # Dynamically inject the contact name into the template
        user_prompt = self.prompt_config.user_prompt_template.format(contact_name=contact_name)

        response = self.client.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.prompt_config.system_instruction},
                {"role": "user", "content": user_prompt},
            ],
        )
        return str(response["message"]["content"])
