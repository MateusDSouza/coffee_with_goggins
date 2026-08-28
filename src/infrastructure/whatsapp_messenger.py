import pywhatkit
import pywhatkit.core.log

from src.interfaces.i_messenger_client import IMessengerClient

pywhatkit.core.log.log_message = lambda *args, **kwargs: None


class WhatsAppMessenger(IMessengerClient):
    def send_message(self, phone_number: str, message: str) -> None:
        pywhatkit.sendwhatmsg_instantly(
            phone_no=phone_number, message=message, wait_time=6, tab_close=True, close_time=2
        )
