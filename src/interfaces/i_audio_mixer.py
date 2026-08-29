from abc import ABC, abstractmethod


class IAudioMixer(ABC):
    """Interface for overlaying background music onto audio tracks."""

    @abstractmethod
    def mix_with_random_background(self, voice_audio_path: str) -> str:
        """Selects a random background track and mixes it with the input voice audio."""
        pass
