from ollama import Client

from src.interfaces.i_llm_client import ILLMClient


class OllamaClient(ILLMClient):
    def __init__(self, host: str = "http://localhost:11434", model_name: str = "dolphin-llama3"):
        self.client = Client(host=host)
        self.model_name = model_name
        self.system_instruction = (
            "You are HoLLyM, a passionate and poetic Catholic evangelizer. "
            "Your mission is to spread the Gospel and remind people of Jesus' infinite love. "
            "You always invite people to repent, go to confession, and receive the Eucharist. "
            "You encourage them to turn away from a life of sin and stand strong with faith. "
            "Keep your tone warm, zealous, and inspiring."
        )

    def generate_message(self, contact_name: str) -> str:
        user_prompt = (
            f"Present yourself. Write a short 'good morning' WhatsApp message for my friend {contact_name}. "
            "Add a versicle of the Holy Bible. Include an emoji. Keep it under 4 sentences."
        )
        response = self.client.chat(
            model=self.model_name,
            messages=[{"role": "system", "content": self.system_instruction}, {"role": "user", "content": user_prompt}],
        )
        return str(response["message"]["content"])
