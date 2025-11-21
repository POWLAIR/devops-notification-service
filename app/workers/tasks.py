from celery import shared_task
from app.services.email import EmailService
from app.services.sms import SMSService
from app.models.notification import Notification, NotificationType, NotificationStatus
from app.database.session import SessionLocal
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

# Initialize services
email_service = EmailService()
sms_service = SMSService()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation_task(self, to_email: str, order_data: dict, tenant_settings: dict):
    """Task Celery pour envoyer email de confirmation de commande"""
    db = SessionLocal()
    
    # Créer l'enregistrement notification
    notification = Notification(
        tenant_id=order_data.get('tenant_id', '00000000-0000-0000-0000-000000000000'),
        type=NotificationType.EMAIL,
        status=NotificationStatus.QUEUED,
        recipient=to_email,
        subject=f"Confirmation de commande #{order_data.get('orderNumber', 'N/A')}",
        content=json.dumps(order_data),
        metadata=json.dumps(tenant_settings)
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    try:
        logger.info(f"📧 Sending order confirmation to {to_email} (notification_id={notification.id})")
        result = email_service.send_order_confirmation(to_email, order_data, tenant_settings)
        
        # Mise à jour: succès
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": result,
            "email": to_email,
            "notification_id": str(notification.id)
        }
        
    except Exception as exc:
        logger.error(f"❌ Failed to send email (notification_id={notification.id}): {exc}")
        
        # Mise à jour: échec
        notification.status = NotificationStatus.FAILED
        notification.error_message = str(exc)
        db.commit()
        
        # Retry avec backoff exponentiel
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    
    finally:
        db.close()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_welcome_email_task(self, to_email: str, user_data: dict, tenant_settings: dict):
    """Task Celery pour envoyer email de bienvenue"""
    db = SessionLocal()
    
    notification = Notification(
        tenant_id=user_data.get('tenant_id', '00000000-0000-0000-0000-000000000000'),
        type=NotificationType.EMAIL,
        status=NotificationStatus.QUEUED,
        recipient=to_email,
        subject=f"Bienvenue sur {tenant_settings.get('name', 'notre plateforme')}",
        content=json.dumps(user_data),
        metadata=json.dumps(tenant_settings)
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    try:
        logger.info(f"📧 Sending welcome email to {to_email} (notification_id={notification.id})")
        result = email_service.send_welcome_email(to_email, user_data, tenant_settings)
        
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": result,
            "email": to_email,
            "notification_id": str(notification.id)
        }
        
    except Exception as exc:
        logger.error(f"❌ Failed to send welcome email (notification_id={notification.id}): {exc}")
        
        notification.status = NotificationStatus.FAILED
        notification.error_message = str(exc)
        db.commit()
        
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    
    finally:
        db.close()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_task(self, to_number: str, message: str):
    """Task Celery pour envoyer SMS"""
    db = SessionLocal()
    
    notification = Notification(
        tenant_id='00000000-0000-0000-0000-000000000000',
        type=NotificationType.SMS,
        status=NotificationStatus.QUEUED,
        recipient=to_number,
        content=message
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    try:
        logger.info(f"📱 Sending SMS to {to_number} (notification_id={notification.id})")
        sid = sms_service.send_sms(to_number, message)
        
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
        notification.metadata = json.dumps({"sid": sid})
        db.commit()
        
        return {
            "success": True,
            "sid": sid,
            "number": to_number,
            "notification_id": str(notification.id)
        }
        
    except Exception as exc:
        logger.error(f"❌ Failed to send SMS (notification_id={notification.id}): {exc}")
        
        notification.status = NotificationStatus.FAILED
        notification.error_message = str(exc)
        db.commit()
        
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    
    finally:
        db.close()


@shared_task(bind=True, max_retries=3)
def send_order_sms_task(self, to_number: str, order_number: str, total: float):
    """Task pour notification de commande par SMS"""
    db = SessionLocal()
    
    notification = Notification(
        tenant_id='00000000-0000-0000-0000-000000000000',
        type=NotificationType.SMS,
        status=NotificationStatus.QUEUED,
        recipient=to_number,
        subject=f"Commande #{order_number}",
        content=f"Commande #{order_number} - {total}€"
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    try:
        logger.info(f"📱 Sending order SMS to {to_number} (notification_id={notification.id})")
        sid = sms_service.send_order_notification(to_number, order_number, total)
        
        notification.status = NotificationStatus.SENT
        notification.sent_at = datetime.utcnow()
        notification.metadata = json.dumps({"sid": sid})
        db.commit()
        
        return {
            "success": True,
            "sid": sid,
            "notification_id": str(notification.id)
        }
        
    except Exception as exc:
        logger.error(f"❌ Failed to send order SMS (notification_id={notification.id}): {exc}")
        
        notification.status = NotificationStatus.FAILED
        notification.error_message = str(exc)
        db.commit()
        
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    
    finally:
        db.close()



