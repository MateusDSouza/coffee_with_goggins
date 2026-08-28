from unittest.mock import MagicMock, patch

import pytest

from src.infrastructure.whatsapp_messenger import WhatsAppMessenger


class TestWhatsAppMessenger:
    """Isolated unit tests for the WhatsApp GUI automation client."""

    @pytest.fixture
    def messenger(self) -> WhatsAppMessenger:
        return WhatsAppMessenger()

    @patch("src.infrastructure.whatsapp_messenger.pywhatkit.sendwhatmsg_instantly")
    def test_send_message_calls_pywhatkit_with_correct_args(
        self, mock_send: MagicMock, messenger: WhatsAppMessenger
    ) -> None:
        """Verifies plain text messaging passes the correct wait and close timings."""
        messenger.send_message("+34627463091", "Hello Maksin!")

        mock_send.assert_called_once_with(
            phone_no="+34627463091", message="Hello Maksin!", wait_time=8, tab_close=True, close_time=2
        )

    @patch("src.infrastructure.whatsapp_messenger.os.path.exists", return_value=False)
    @patch("src.infrastructure.whatsapp_messenger.os.path.abspath", return_value="/fake/path.mp3")
    def test_send_audio_raises_error_if_file_missing(
        self, mock_abspath: MagicMock, mock_exists: MagicMock, messenger: WhatsAppMessenger
    ) -> None:
        """Ensures the process fails fast before attempting to open the browser if the file is missing."""
        with pytest.raises(FileNotFoundError, match="Audio file not found: /fake/path.mp3"):
            messenger.send_audio("+34627463091", "dummy.mp3")

    @pytest.mark.parametrize(
        ("platform", "expected_paste_key", "expected_close_key"),
        [
            ("darwin", "command", "command"),
            ("win32", "ctrl", "ctrl"),
            ("linux", "ctrl", "ctrl"),
        ],
    )
    @patch("src.infrastructure.whatsapp_messenger.time.sleep")
    @patch("src.infrastructure.whatsapp_messenger.WhatsAppMessenger._copy_file_to_clipboard")
    @patch("src.infrastructure.whatsapp_messenger.pyautogui")
    @patch("src.infrastructure.whatsapp_messenger.pywhatkit.sendwhatmsg_instantly")
    @patch("src.infrastructure.whatsapp_messenger.os.path.exists", return_value=True)
    @patch("src.infrastructure.whatsapp_messenger.os.path.abspath", return_value="/fake/audio.mp3")
    def test_send_audio_executes_gui_workflow_correctly(
        self,
        mock_abspath: MagicMock,
        mock_exists: MagicMock,
        mock_sendwhatmsg: MagicMock,
        mock_pyautogui: MagicMock,
        mock_copy: MagicMock,
        mock_sleep: MagicMock,
        messenger: WhatsAppMessenger,
        platform: str,
        expected_paste_key: str,
        expected_close_key: str,
    ) -> None:
        """Verifies the precise sequence of browser opening, copying, pasting, and closing across OS platforms."""

        with patch("src.infrastructure.whatsapp_messenger.sys.platform", platform):
            messenger.send_audio("+34627463091", "audio.mp3")

        # 1. Assert intro text was sent and browser kept open
        mock_sendwhatmsg.assert_called_once_with(
            phone_no="+34627463091", message="Sending a voice note...", wait_time=10, tab_close=False
        )

        # 2. Assert clipboard copy was triggered
        mock_copy.assert_called_once_with("/fake/audio.mp3")

        # 3. Assert GUI automation used the correct OS hotkeys
        assert mock_pyautogui.hotkey.call_count == 2
        mock_pyautogui.hotkey.assert_any_call(expected_paste_key, "v")
        mock_pyautogui.hotkey.assert_any_call(expected_close_key, "w")
        mock_pyautogui.press.assert_called_once_with("enter")

        # 4. Assert sleep was called to allow UI to catch up
        assert mock_sleep.call_count == 3

    @patch("src.infrastructure.whatsapp_messenger.subprocess.run")
    def test_copy_file_to_clipboard_macos(self, mock_subprocess: MagicMock, messenger: WhatsAppMessenger) -> None:
        """Verifies AppleScript is utilized for macOS clipboards."""
        with patch("src.infrastructure.whatsapp_messenger.sys.platform", "darwin"):
            messenger._copy_file_to_clipboard("/fake/file.mp3")

        mock_subprocess.assert_called_once_with(
            ["osascript", "-e", 'set the clipboard to POSIX file "/fake/file.mp3"'], check=True
        )

    @patch("src.infrastructure.whatsapp_messenger.subprocess.run")
    def test_copy_file_to_clipboard_windows(self, mock_subprocess: MagicMock, messenger: WhatsAppMessenger) -> None:
        """Verifies PowerShell is utilized for Windows clipboards."""
        with patch("src.infrastructure.whatsapp_messenger.sys.platform", "win32"):
            messenger._copy_file_to_clipboard("/fake/file.mp3")

        mock_subprocess.assert_called_once_with(
            ["powershell", "-command", 'Set-Clipboard -Path "/fake/file.mp3"'], check=True
        )

    def test_copy_file_to_clipboard_unsupported_os(self, messenger: WhatsAppMessenger) -> None:
        """Ensures Linux or other unsupported OS environments fail gracefully rather than executing shell commands."""
        with patch("src.infrastructure.whatsapp_messenger.sys.platform", "linux"):
            with pytest.raises(NotImplementedError, match="Clipboard file copying is not supported on OS: linux"):
                messenger._copy_file_to_clipboard("/fake/file.mp3")
