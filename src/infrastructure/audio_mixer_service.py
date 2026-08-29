import logging
import random
from pathlib import Path

from pydub import AudioSegment  # type: ignore[import-untyped]

from src.interfaces.i_audio_mixer import IAudioMixer

logger = logging.getLogger(__name__)


class AudioMixerService(IAudioMixer):
    """Concrete implementation for selecting and mixing background audio."""

    def __init__(
        self,
        songs_dir: str = "background_songs",
        bg_volume_db: int = -18,
    ) -> None:
        self.songs_dir = Path(songs_dir)
        self.bg_volume_db = bg_volume_db

    def get_random_background_track(self) -> Path | None:
        """Discovers and randomly selects an MP3 or M4A background track."""
        if not self.songs_dir.exists():
            return None

        # Search for both .mp3 and .m4a files
        audio_files = [f for f in self.songs_dir.iterdir() if f.suffix.lower() in [".mp3", ".m4a"]]

        if not audio_files:
            return None

        return random.choice(audio_files)

    def adjust_background_length(
        self, bg_music: AudioSegment, target_duration_ms: int, fade_out_ms: int = 1000
    ) -> AudioSegment:
        """Trims or loops background audio to match the voice track duration precisely."""
        if len(bg_music) < target_duration_ms:
            loops = (target_duration_ms // len(bg_music)) + 1
            bg_music = (bg_music * loops)[:target_duration_ms]
        else:
            bg_music = bg_music[:target_duration_ms]

        return bg_music.fade_out(fade_out_ms)

    def mix_audio_segments(self, voice: AudioSegment, bg_music: AudioSegment) -> AudioSegment:
        """Adjusts background volume, aligns track lengths, and overlays voice on top."""
        adjusted_bg = bg_music + self.bg_volume_db
        fitted_bg = self.adjust_background_length(adjusted_bg, len(voice))
        return fitted_bg.overlay(voice)

    def mix_with_random_background(self, voice_audio_path: str) -> str:
        """Orchestrates track selection, audio loading, mixing, and saving."""
        voice_path = Path(voice_audio_path)
        if not voice_path.exists():
            logger.error(f"Voice audio file not found: {voice_path}")
            raise FileNotFoundError(f"Voice file not found: {voice_path}")

        bg_track_path = self.get_random_background_track()
        if not bg_track_path:
            logger.warning(f"Proceeding with unmixed raw voice audio for: {voice_path}")
            return str(voice_path)

        voice_segment = AudioSegment.from_file(voice_path)
        bg_segment = AudioSegment.from_file(bg_track_path)

        mixed_segment = self.mix_audio_segments(voice_segment, bg_segment)
        mixed_segment.export(voice_path, format="mp3")

        logger.info(f"Successfully mixed background audio into {voice_path}")
        return str(voice_path)
