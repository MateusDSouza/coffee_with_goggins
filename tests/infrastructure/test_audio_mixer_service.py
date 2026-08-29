from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydub import AudioSegment  # type: ignore[import-untyped]

from src.infrastructure.audio_mixer_service import AudioMixerService


class TestAudioMixerService:
    """Isolated unit tests for individual audio mixing helpers."""

    @pytest.fixture
    def mixer(self, tmp_path: Path) -> AudioMixerService:
        return AudioMixerService(songs_dir=str(tmp_path), bg_volume_db=-20)

    def test_get_random_background_track_returns_none_when_empty(self, mixer: AudioMixerService) -> None:
        assert mixer.get_random_background_track() is None

    def test_get_random_background_track_returns_file(self, mixer: AudioMixerService, tmp_path: Path) -> None:
        song = tmp_path / "song1.mp3"
        song.touch()

        selected = mixer.get_random_background_track()
        assert selected == song

    def test_adjust_background_length_loops_short_track(self, mixer: AudioMixerService) -> None:
        short_bg = MagicMock(spec=AudioSegment)
        short_bg.__len__.return_value = 2000
        short_bg.__mul__.return_value = short_bg
        short_bg.__getitem__.return_value = short_bg
        short_bg.fade_out.return_value = short_bg

        result = mixer.adjust_background_length(short_bg, target_duration_ms=5000)

        assert result is not None
        short_bg.__mul__.assert_called_once_with(3)
        short_bg.fade_out.assert_called_once_with(1000)

    @patch("src.infrastructure.audio_mixer_service.AudioSegment.from_file")
    def test_mix_with_random_background_returns_unmixed_if_no_songs(
        self, mock_from_file: MagicMock, mixer: AudioMixerService, tmp_path: Path
    ) -> None:
        # Arrange: Ensure songs_dir points to an isolated directory with no MP3 files
        empty_songs_dir = tmp_path / "empty_songs"
        empty_songs_dir.mkdir()
        mixer.songs_dir = empty_songs_dir

        voice_file = tmp_path / "voice.mp3"
        voice_file.touch()

        # Act
        result = mixer.mix_with_random_background(str(voice_file))

        # Assert
        assert result == str(voice_file)
        mock_from_file.assert_not_called()
