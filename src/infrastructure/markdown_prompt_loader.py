from pathlib import Path

from src.models.prompt_config import PromptConfig


class MarkdownPromptLoader:
    """Parses a specifically formatted Markdown file into a PromptConfig."""

    @staticmethod
    def load(file_path: str | Path) -> PromptConfig:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")

        system_text: list[str] = []
        user_text: list[str] = []
        current_section: str | None = None

        with open(path, encoding="utf-8") as f:
            for line in f:
                normalized_line = line.strip().lower()
                if normalized_line.startswith("# system"):
                    current_section = "system"
                    continue
                elif normalized_line.startswith("# user"):
                    current_section = "user"
                    continue

                # Append lines to the appropriate section based on the current header
                if current_section == "system":
                    system_text.append(line)
                elif current_section == "user":
                    user_text.append(line)

        # Join the lines, stripping leading/trailing whitespace but preserving internal line breaks
        return PromptConfig(
            system_instruction="".join(system_text).strip(), user_prompt_template="".join(user_text).strip()
        )
