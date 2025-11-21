from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
from app.workers.tasks import (
    send_order_confirmation_task,
    send_welcome_email_task,
    send_sms_task,
    send_order_sms_task
)

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



