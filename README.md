# Notification Service (Python)

Service de notifications (emails/SMS) pour la plateforme SaaS multi-tenant.

## Description

Le Notification Service gère :
- Emails transactionnels (SendGrid)
- SMS notifications (Twilio)
- Queue asynchrone (Celery + Redis)
- Templates personnalisables par tenant (Jinja2)
- Retry logic avec backoff exponentiel

## Technologies

- **Langage** : Python 3.11+
- **Framework** : FastAPI
- **Queue** : Celery + Redis
- **Email** : SendGrid SDK
- **SMS** : Twilio SDK
- **Templates** : Jinja2
- **Port** : 6000

## Pourquoi Python ?

✅ **SendGrid SDK Python** : Le plus complet et maintenu  
✅ **Twilio SDK Python** : API la plus riche  
✅ **Celery** : Queue asynchrone mature (meilleure que Bull)  
✅ **Jinja2** : Templating puissant pour emails  
✅ **Cohérence** : Même stack que Auth Service  

## Installation

```bash
# Créer venv
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt

# Copier .env
cp .env.example .env

# Lancer l'API
uvicorn app.main:app --reload --host 0.0.0.0 --port 6000

# Lancer Celery worker (dans un autre terminal)
celery -A app.workers.celery_app worker --loglevel=info
```

## Variables d'environnement

```env
# Server
PORT=6000
HOST=0.0.0.0
ENV=development

# Database
DATABASE_URL=postgresql://saas_admin:password@postgres:5432/saas_platform

# Redis (pour Celery)
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# SendGrid
SENDGRID_API_KEY=SG.xxx
SENDGRID_FROM_EMAIL=noreply@votreplateforme.com
SENDGRID_FROM_NAME=Votre Plateforme

# Twilio
TWILIO_ACCOUNT_SID=ACxxx
TWILIO_AUTH_TOKEN=xxx
TWILIO_PHONE_NUMBER=+33123456789
```

## Structure du projet

```
notification-service/
├── app/
│   ├── main.py                  # FastAPI app
│   ├── api/
│   │   └── routes/
│   │       ├── notifications.py
│   │       └── health.py
│   ├── services/
│   │   ├── email.py             # SendGrid service
│   │   └── sms.py               # Twilio service
│   ├── workers/
│   │   ├── celery_app.py        # Celery config
│   │   └── tasks.py             # Celery tasks
│   ├── models/
│   │   └── notification.py      # SQLAlchemy models
│   ├── database/
│   │   └── session.py
│   ├── config/
│   │   └── settings.py
│   └── templates/               # Jinja2 templates
│       ├── order_confirmation.html
│       ├── welcome.html
│       └── password_reset.html
├── requirements.txt
├── Dockerfile
└── README.md
```

## Endpoints API

### POST /notifications/order-confirmation
Envoyer email de confirmation de commande

**Request:**
```json
{
  "email": "customer@example.com",
  "orderData": {
    "orderNumber": "ORD-20250119-000001",
    "total": 100.00,
    "items": [...]
  },
  "tenantSettings": {
    "name": "Mon Shop",
    "emailFrom": "noreply@mon-shop.com"
  }
}
```

### POST /notifications/welcome-email
Envoyer email de bienvenue

### POST /notifications/sms
Envoyer SMS

## Templates Jinja2

Les templates sont dans `app/templates/` :

```html
<!-- app/templates/order_confirmation.html -->
<!DOCTYPE html>
<html>
<body>
  <h1>{{ tenant.name }}</h1>
  <h2>Merci pour votre commande !</h2>
  <p>Numéro : <strong>#{{ order.orderNumber }}</strong></p>
  <p>Total : <strong>{{ order.total }} €</strong></p>
  
  <ul>
    {% for item in order.items %}
    <li>{{ item.productName }} x{{ item.quantity }} - {{ item.totalPrice }} €</li>
    {% endfor %}
  </ul>
</body>
</html>
```

## Celery Tasks

```python
# app/workers/tasks.py
from celery import shared_task
from app.services.email import send_order_confirmation

@shared_task(bind=True, max_retries=3)
def send_order_confirmation_task(self, email, order_data, tenant_settings):
    try:
        send_order_confirmation(email, order_data, tenant_settings)
    except Exception as exc:
        # Retry avec backoff exponentiel
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
```

## Performance

- **Async** : FastAPI + Celery pour traitement non-bloquant
- **Retry** : Backoff exponentiel automatique
- **Rate limiting** : Respect des limites SendGrid/Twilio
- **Batch** : Possibilité d'envois groupés

## Tests

```bash
# Tests unitaires
pytest

# Tests avec coverage
pytest --cov=app tests/

# Tests d'intégration
pytest tests/integration/
```

## Docker

```bash
# Build
docker build -t notification-service:latest .

# Run API + Worker
docker-compose up notification-service notification-worker
```

## Documentation

Voir [Phase 2](../transform/phase-2-nouveaux-services.md) pour l'implémentation complète.

## License

MIT
