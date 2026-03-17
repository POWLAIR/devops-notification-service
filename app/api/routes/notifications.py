from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.workers.tasks import (
    send_order_confirmation_task,
    send_welcome_email_task,
    send_sms_task,
    send_order_sms_task
)
from app.database.session import get_db
from app.models.notification import Notification, NotificationType, NotificationStatus

router = APIRouter(prefix="/notifications", tags=["notifications"])


# Request models
class OrderConfirmationRequest(BaseModel):
    email: EmailStr
    order_data: Dict
    tenant_settings: Dict


class WelcomeEmailRequest(BaseModel):
    email: EmailStr
    user_data: Dict
    tenant_settings: Dict


class SMSRequest(BaseModel):
    phone_number: str
    message: str


class OrderSMSRequest(BaseModel):
    phone_number: str
    order_number: str
    total: float


# Routes
@router.post("/order-confirmation")
async def send_order_confirmation(request: OrderConfirmationRequest):
    """Envoyer email de confirmation de commande (async avec Celery)"""
    try:
        # Queue the task
        task = send_order_confirmation_task.delay(
            request.email,
            request.order_data,
            request.tenant_settings
        )
        
        return {
            "message": "Order confirmation email queued",
            "task_id": task.id,
            "email": request.email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue email: {str(e)}")


@router.post("/welcome-email")
async def send_welcome_email(request: WelcomeEmailRequest):
    """Envoyer email de bienvenue (async avec Celery)"""
    try:
        task = send_welcome_email_task.delay(
            request.email,
            request.user_data,
            request.tenant_settings
        )
        
        return {
            "message": "Welcome email queued",
            "task_id": task.id,
            "email": request.email
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue email: {str(e)}")


@router.post("/sms")
async def send_sms(request: SMSRequest):
    """Envoyer SMS (async avec Celery)"""
    try:
        task = send_sms_task.delay(
            request.phone_number,
            request.message
        )
        
        return {
            "message": "SMS queued",
            "task_id": task.id,
            "phone_number": request.phone_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue SMS: {str(e)}")


@router.post("/order-sms")
async def send_order_sms(request: OrderSMSRequest):
    """Envoyer notification de commande par SMS"""
    try:
        task = send_order_sms_task.delay(
            request.phone_number,
            request.order_number,
            request.total
        )
        
        return {
            "message": "Order SMS queued",
            "task_id": task.id,
            "phone_number": request.phone_number
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue SMS: {str(e)}")


@router.get("/unread-count")
async def get_unread_count(
    tenant_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retourne le nombre de notifications non traitées (PENDING + QUEUED)"""
    query = db.query(func.count(Notification.id)).filter(
        Notification.status.in_([NotificationStatus.PENDING, NotificationStatus.QUEUED])
    )
    if tenant_id:
        query = query.filter(Notification.tenant_id == tenant_id)
    count = query.scalar() or 0
    return {"count": count}


@router.get("/history")
async def get_notifications_history(
    tenant_id: Optional[str] = None,
    status: Optional[NotificationStatus] = None,
    type: Optional[NotificationType] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Récupérer l'historique des notifications avec filtres"""
    query = db.query(Notification)
    
    if tenant_id:
        query = query.filter(Notification.tenant_id == tenant_id)
    
    if status:
        query = query.filter(Notification.status == status)
    
    if type:
        query = query.filter(Notification.type == type)
    
    total = query.count()
    notifications = query.order_by(
        Notification.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "notifications": [
            {
                "id": str(n.id),
                "tenant_id": str(n.tenant_id),
                "type": n.type,
                "status": n.status,
                "recipient": n.recipient,
                "subject": n.subject,
                "error_message": n.error_message,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "sent_at": n.sent_at.isoformat() if n.sent_at else None
            }
            for n in notifications
        ]
    }


@router.get("/stats")
async def get_notifications_stats(
    tenant_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Statistiques sur les notifications"""
    query = db.query(
        Notification.status,
        Notification.type,
        func.count(Notification.id).label('count')
    )
    
    if tenant_id:
        query = query.filter(Notification.tenant_id == tenant_id)
    
    results = query.group_by(
        Notification.status,
        Notification.type
    ).all()
    
    stats = {
        "by_status": {},
        "by_type": {},
        "detailed": []
    }
    
    for status, type, count in results:
        # Par statut
        if status not in stats["by_status"]:
            stats["by_status"][status] = 0
        stats["by_status"][status] += count
        
        # Par type
        if type not in stats["by_type"]:
            stats["by_type"][type] = 0
        stats["by_type"][type] += count
        
        # Détaillé
        stats["detailed"].append({
            "status": status,
            "type": type,
            "count": count
        })
    
    return stats



