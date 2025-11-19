from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Notification Service",
    description="Service de notifications (Email/SMS) pour Multi-Tenant SaaS",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3001").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "notification-service"
    }

@app.post("/notifications/order-confirmation")
async def send_order_confirmation():
    """Envoyer email de confirmation de commande"""
    # TODO: Implement with Celery task
    return {"message": "Order confirmation email queued"}

@app.post("/notifications/welcome-email")
async def send_welcome_email():
    """Envoyer email de bienvenue"""
    # TODO: Implement with Celery task
    return {"message": "Welcome email queued"}

@app.post("/notifications/sms")
async def send_sms():
    """Envoyer SMS"""
    # TODO: Implement with Celery task
    return {"message": "SMS queued"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 6000))
    uvicorn.run(app, host="0.0.0.0", port=port)

