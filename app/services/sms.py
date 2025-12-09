from twilio.rest import Client
import os
import logging

logger = logging.getLogger(__name__)


class SMSService:
    def __init__(self):
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        # Détecter les valeurs placeholder ou vides
        is_placeholder = (
            not account_sid or not auth_token or
            account_sid.startswith('ACDEV_MODE') or account_sid.startswith('ACPLACEHOLDER') or
            auth_token.startswith('DEV_MODE') or auth_token.startswith('PLACEHOLDER')
        )
        
        if is_placeholder:
            self.client = None
        else:
            self.client = Client(account_sid, auth_token)
        
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER', '+33600000000')
    
    def send_sms(self, to_number: str, message: str) -> str:
        """Envoyer SMS via Twilio"""
        try:
            if self.client:
                msg = self.client.messages.create(
                    to=to_number,
                    from_=self.from_number,
                    body=message
                )
                logger.info(f"✅ SMS sent to {to_number} - SID: {msg.sid}")
                return msg.sid
            else:
                logger.warning(f"⚠️ SMS simulation (Twilio not configured): {to_number}")
                return "simulated-sid"
                
        except Exception as e:
            logger.error(f"❌ Error sending SMS: {e}")
            raise
    
    def send_order_notification(self, to_number: str, order_number: str, total: float) -> str:
        """Envoyer notification de commande par SMS"""
        message = f"Votre commande #{order_number} a été confirmée. Montant: {total}€. Merci !"
        return self.send_sms(to_number, message)



