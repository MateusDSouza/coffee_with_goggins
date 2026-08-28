import os
import subprocess
import sys
import time

import pyautogui  # type: ignore
import pywhatkit
import pywhatkit.core.log

from src.interfaces.i_messenger_client import IMessengerClient

pywhatkit.core.log.log_message = lambda *args, **kwargs: None


class WhatsAppMessenger(IMessengerClient):
    """Concrete implementation for sending messages and media via WhatsApp Web."""

    def send_message(self, phone_number: str, message: str) -> None:
        pywhatkit.sendwhatmsg_instantly(  # type: ignore[attr-defined]
            phone_no=phone_number, message=message, wait_time=8, tab_close=True, close_time=2
        )

    def send_audio(self, phone_number: str, audio_file_path: str) -> None:
        """Sends an audio file by safely copying it to the OS clipboard and pasting it."""

        abs_path = os.path.abspath(audio_file_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Audio file not found: {abs_path}")

        print(f"🌐 Opening WhatsApp Web for audio to {phone_number}...")

        # 1. Open chat and send introductory text.
        pywhatkit.sendwhatmsg_instantly(  # type: ignore[attr-defined]
            phone_no=phone_number, message="🎤 Sending a voice note...", wait_time=10, tab_close=False
        )

        # 2. Copy the file to the system clipboard
        self._copy_file_to_clipboard(abs_path)

        # 3. Ensure the browser text box is focused, then paste
        time.sleep(1)
        if sys.platform == "darwin":
            pyautogui.hotkey("command", "v")  # macOS paste
        else:
            pyautogui.hotkey("ctrl", "v")  # Windows/Linux paste

        # 4. Wait for the WhatsApp Web media preview to load, then send
        time.sleep(2)
        pyautogui.press("enter")
        print(f"🎉 Audio file {audio_file_path} dispatched!")

        # 5. Clean up by closing the browser tab
        time.sleep(2)
        if sys.platform == "darwin":
            pyautogui.hotkey("command", "w")
        else:
            pyautogui.hotkey("ctrl", "w")

    def _copy_file_to_clipboard(self, file_path: str) -> None:
        """Cross-platform method to copy a physical file into the system clipboard."""
        if sys.platform == "darwin":
            # macOS: Use AppleScript to copy the file reference
            script = f'set the clipboard to POSIX file "{file_path}"'
            subprocess.run(["osascript", "-e", script], check=True)
        elif sys.platform == "win32":
            # Windows: Use PowerShell to copy the file
            subprocess.run(["powershell", "-command", f'Set-Clipboard -Path "{file_path}"'], check=True)
        else:
            raise NotImplementedError(f"Clipboard file copying is not supported on OS: {sys.platform}")
