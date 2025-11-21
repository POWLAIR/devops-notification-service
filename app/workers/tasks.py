from celery import shared_task
from app.services.email import EmailService
from app.services.sms import SMSService
import logging

logger = logging.getLogger(__name__)

# Initialize services
email_service = EmailService()
sms_service = SMSService()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation_task(self, to_email: str, order_data: dict, tenant_settings: dict):
    """Task Celery pour envoyer email de confirmation de commande"""
    try:
        logger.info(f"📧 Sending order confirmation to {to_email}")
        result = email_service.send_order_confirmation(to_email, order_data, tenant_settings)
        return {"success": result, "email": to_email}
    except Exception as exc:
        logger.error(f"❌ Failed to send email: {exc}")
        # Retry avec backoff exponentiel
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email_task(self, to_email: str, user_data: dict, tenant_settings: dict):
    """Task Celery pour envoyer email de bienvenue"""
    try:
        logger.info(f"📧 Sending welcome email to {to_email}")
        result = email_service.send_welcome_email(to_email, user_data, tenant_settings)
        return {"success": result, "email": to_email}
    except Exception as exc:
        logger.error(f"❌ Failed to send welcome email: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_task(self, to_number: str, message: str):
    """Task Celery pour envoyer SMS"""
    try:
        logger.info(f"📱 Sending SMS to {to_number}")
        sid = sms_service.send_sms(to_number, message)
        return {"success": True, "sid": sid, "number": to_number}
    except Exception as exc:
        logger.error(f"❌ Failed to send SMS: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@shared_task(bind=True, max_retries=3)
def send_order_sms_task(self, to_number: str, order_number: str, total: float):
    """Task pour notification de commande par SMS"""
    try:
        logger.info(f"📱 Sending order SMS to {to_number}")
        sid = sms_service.send_order_notification(to_number, order_number, total)
        return {"success": True, "sid": sid}
    except Exception as exc:
        logger.error(f"❌ Failed to send order SMS: {exc}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)

