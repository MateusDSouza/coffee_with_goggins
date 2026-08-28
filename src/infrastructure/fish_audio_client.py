import logging
from pathlib import Path

import requests

from src.interfaces.i_text_to_speech_client import ITextToSpeechClient

logger = logging.getLogger(__name__)


class FishAudioTTSClient(ITextToSpeechClient):
    """An HTTP client that communicates with the Fish Audio API using the explicit free tier model."""

    def __init__(
        self,
        api_key: str,
        voice_id: str | None = None,
        model: str = "s2.1-pro-free",
        output_dir: str = "output_audio",
    ) -> None:
        self.api_key = api_key
        self.voice_id = voice_id
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.api_url = "https://api.fish.audio/v1/tts"

        logger.debug(f"Initialized FishAudioTTSClient with model {self.model} and output directory {self.output_dir}")

    def generate_audio(self, text: str, contact_name: str) -> str:
        output_path = self.output_dir / f"message_{contact_name}.mp3"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "text": text,
            "format": "mp3",
            "model": self.model,
        }

        if self.voice_id:
            payload["reference_id"] = self.voice_id

        logger.info(f"Requesting audio generation for contact: {contact_name}")

        response = requests.post(self.api_url, headers=headers, json=payload, stream=True)
        response.raise_for_status()

        logger.debug(f"Stream established. Writing to {output_path}")

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Audio successfully saved to {output_path}")

        return str(output_path)
