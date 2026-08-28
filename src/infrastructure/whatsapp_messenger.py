import logging
import os
import subprocess
import sys
import textwrap
import time
import webbrowser  # Added standard library import

import pyautogui  # type: ignore
import pywhatkit
import pywhatkit.core.log

from src.interfaces.i_messenger_client import IMessengerClient

logger = logging.getLogger(__name__)

pywhatkit.core.log.log_message = lambda *args, **kwargs: None


class WhatsAppMessenger(IMessengerClient):
    """Concrete implementation for sending messages and media via WhatsApp Web."""

    def send_message(self, phone_number: str, message: str) -> None:
        logger.info(f"Dispatching WhatsApp text message to {phone_number}")
        pywhatkit.sendwhatmsg_instantly(  # type: ignore[attr-defined]
            phone_no=phone_number, message=message, wait_time=8, tab_close=True, close_time=2
        )
        logger.debug(f"Text message successfully dispatched to {phone_number}")

    def send_audio(self, phone_number: str, audio_file_path: str) -> None:
        """Sends an audio file by safely copying it to the OS clipboard and pasting it."""

        abs_path = os.path.abspath(audio_file_path)
        if not os.path.exists(abs_path):
            logger.error(f"Audio file not found: {abs_path}")
            raise FileNotFoundError(f"Audio file not found: {abs_path}")

        logger.info(f"Opening WhatsApp Web for audio dispatch to {phone_number}")

        # 1. Open the direct WhatsApp Web chat link without sending text
        clean_phone = phone_number.replace("+", "").strip()
        chat_url = f"https://web.whatsapp.com/send?phone={clean_phone}"
        webbrowser.open(chat_url)

        # 2. Wait for WhatsApp Web UI to load completely
        time.sleep(10)

        # 3. Copy the file to the system clipboard
        self._copy_file_to_clipboard(abs_path)

        # 4. Paste the file directly into the chat
        time.sleep(1)
        if sys.platform == "darwin":
            pyautogui.hotkey("command", "v")  # macOS paste
        else:
            pyautogui.hotkey("ctrl", "v")  # Windows/Linux paste

        # 5. Wait for media preview, then send
        time.sleep(2)
        pyautogui.press("enter")
        logger.info(f"Audio file {audio_file_path} dispatched to {phone_number}")

        # 6. Clean up by closing the browser tab
        time.sleep(2)
        if sys.platform == "darwin":
            pyautogui.hotkey("command", "w")
        else:
            pyautogui.hotkey("ctrl", "w")

    def _copy_file_to_clipboard(self, file_path: str) -> None:
        """Cross-platform method to copy a physical file into the system clipboard."""
        logger.debug(f"Copying file {file_path} to system clipboard on platform: {sys.platform}")
        if sys.platform == "darwin":
            swift_script = textwrap.dedent(
                f"""\
                use framework "AppKit"
                use scripting additions

                set thePath to "{file_path}"
                set theURL to current application's NSURL's fileURLWithPath:thePath
                set theBoard to current application's NSPasteboard's generalPasteboard()
                theBoard's clearContents()
                theBoard's writeObjects:{{theURL}}
                """
            )
            subprocess.run(["osascript", "-e", swift_script], check=True)
        elif sys.platform == "win32":
            subprocess.run(["powershell", "-command", f'Set-Clipboard -Path "{file_path}"'], check=True)
        else:
            logger.error(f"Clipboard file copying not supported on platform: {sys.platform}")
            raise NotImplementedError(f"Clipboard file copying is not supported on OS: {sys.platform}")
