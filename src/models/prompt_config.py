from dataclasses import dataclass


@dataclass
class PromptConfig:
    """Holds the system instructions and user templates for the LLM."""

    system_instruction: str
    user_prompt_template: str
