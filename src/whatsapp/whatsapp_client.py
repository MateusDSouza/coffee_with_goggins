import pywhatkit

# ==========================================
# DISABLE PYWHATKIT TEXT LOGGING
# ==========================================
# This prevents pywhatkit from generating PyWhatKit_DB.txt locally.
import pywhatkit.core.log

pywhatkit.core.log.log_message = lambda *args, **kwargs: None


# ==========================================
# MESSAGE SENDING LOGIC
# ==========================================
def send_whatsapp_message(phone_number: str, message: str):
    """
    Opens the browser, types the message, and hits enter.
    """
    print(f"🌐 Opening WhatsApp Web to send message to {phone_number}...")

    # Send the message using the fast settings optimized for your Mac
    pywhatkit.sendwhatmsg_instantly(
        phone_no=phone_number,
        message=message,
        wait_time=6,
        tab_close=True,
        close_time=2,
    )
    print("🎉 Message sent!\n")
