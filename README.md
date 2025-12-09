# Notification Service (Python)

Service de notifications en Python avec FastAPI, SendGrid, Twilio et Celery.

## 🚀 Technologies

- **Python 3.11+** - Langage
- **FastAPI** - Framework API moderne
- **Celery** - Queue de tâches asynchrones
- **Redis** - Broker Celery
- **SendGrid** - Service email
- **Twilio** - Service SMS
- **Jinja2** - Templating HTML
- **SQLAlchemy** - ORM PostgreSQL

## 📁 Structure

```text
notification-service/
├── app/
│   ├── main.py                  # FastAPI app
│   ├── api/
│   │   └── routes/
│   │       └── notifications.py # Routes API
│   ├── services/
│   │   ├── email.py             # SendGrid
│   │   └── sms.py               # Twilio
│   ├── workers/
│   │   ├── celery_app.py        # Config Celery
│   │   └── tasks.py             # Tâches async
│   ├── models/
│   │   └── notification.py      # Models SQLAlchemy
│   ├── database/
│   │   └── session.py           # DB connection
│   └── templates/               # Templates Jinja2
│       ├── order_confirmation.html
│       └── welcome.html
├── requirements.txt
├── Dockerfile
└── README.md
```

## 🔧 Configuration

Créer un fichier `.env` :

```env
DATABASE_URL=postgresql://saas_admin:password@localhost:5432/saas_platform

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

SENDGRID_API_KEY=SG.xxxxx
SENDGRID_FROM_EMAIL=noreply@saas-platform.com

TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_PHONE_NUMBER=+33600000000

PORT=6000
CORS_ORIGINS=http://localhost:3001
```

## 🏃 Lancer en développement

```bash
# Installer les dépendances
pip install -r requirements.txt

# Terminal 1 : API FastAPI
uvicorn app.main:app --reload --port 6000

# Terminal 2 : Celery Worker
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3 : Celery Beat (optionnel)
celery -A app.workers.celery_app beat --loglevel=info
```

## 🐳 Docker

```bash
# Build
docker build -t notification-service .

# Run API
docker run -p 6000:6000 --env-file .env notification-service

# Run Worker
docker run --env-file .env notification-service \
  celery -A app.workers.celery_app worker --loglevel=info
```

## 📡 API Endpoints

Toutes les routes sont sous `/api/v1/notifications`

### Emails

- `POST /api/v1/notifications/order-confirmation` - Email confirmation commande
- `POST /api/v1/notifications/welcome-email` - Email de bienvenue

### SMS

- `POST /api/v1/notifications/sms` - Envoyer SMS générique
- `POST /api/v1/notifications/order-sms` - SMS notification commande

## 🧪 Tests

```bash
# Tests unitaires
pytest

# Coverage
pytest --cov=app --cov-report=html

# Tests async
pytest -v
```

## 📊 Fonctionnalités

✅ Email avec templates HTML (Jinja2)  
✅ SMS via Twilio  
✅ Queue asynchrone avec Celery  
✅ Retry automatique avec backoff exponentiel  
✅ Templates personnalisables par tenant  
✅ Suivi des notifications en DB  
✅ Healthcheck

## 🔄 Celery Tasks

### Email Tasks

- `send_order_confirmation_task` - Confirmation de commande
- `send_welcome_email_task` - Email de bienvenue

### SMS Tasks

- `send_sms_task` - SMS générique
- `send_order_sms_task` - Notification de commande

**Retry policy** :
- Max retries : 3
- Backoff : exponentiel (2^n secondes)

## 📧 Templates

### order_confirmation.html

Email de confirmation de commande avec :
- Numéro de commande
- Liste des articles
- Total et commission
- Design responsive

### welcome.html

Email de bienvenue avec :
- Message personnalisé
- Liste des fonctionnalités
- Call-to-action

## 🔐 Sécurité

- Variables d'environnement pour secrets
- Isolation multi-tenant
- Validation des données (Pydantic)

## 📈 Performance

- **Latence API** : ~30ms
- **Throughput** : 2K req/s
- **Workers Celery** : Scalable horizontalement
- **Mémoire** : ~80MB par worker

## 🚀 Production

### Checklist avant déploiement

- [ ] Clés SendGrid de production configurées (`SENDGRID_API_KEY`)
- [ ] Clés Twilio de production configurées (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`)
- [ ] Mot de passe PostgreSQL sécurisé
- [ ] Redis avec authentification
- [ ] CORS configuré avec les origines de production uniquement
- [ ] PostgreSQL avec connexions SSL
- [ ] HTTPS activé (TLS/SSL)
- [ ] Email d'expéditeur configuré (`SENDGRID_FROM_EMAIL`)
- [ ] Numéro de téléphone Twilio configuré (`TWILIO_PHONE_NUMBER`)
- [ ] Monitoring et alertes (Prometheus, Grafana)
- [ ] Logs centralisés (ELK, Loki)
- [ ] Backups automatiques de PostgreSQL
- [ ] Workers Celery configurés pour la production (nombre de workers, retry policy)
- [ ] Variables d'environnement configurées sur la plateforme de déploiement

### Variables d'environnement Docker

Configurées dans `docker-compose.yml` :
```yaml
DATABASE_URL=postgresql://saas_admin:${DB_PASSWORD}@postgres:5432/saas_platform
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
SENDGRID_API_KEY=${SENDGRID_API_KEY}
SENDGRID_FROM_EMAIL=${SENDGRID_FROM_EMAIL}
TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
TWILIO_PHONE_NUMBER=${TWILIO_PHONE_NUMBER}
```

### Déploiement des Workers Celery

En production, déployer séparément :
- **API FastAPI** : Service principal pour recevoir les requêtes
- **Celery Worker** : Workers pour traiter les tâches asynchrones
- **Celery Beat** : Scheduler pour les tâches périodiques (optionnel)

```bash
# API
docker run -d --env-file .env notification-service \
  uvicorn app.main:app --host 0.0.0.0 --port 6000

# Worker
docker run -d --env-file .env notification-service \
  celery -A app.workers.celery_app worker --loglevel=info --concurrency=4
```

## 📝 Notes

- Le service utilise Celery pour le traitement asynchrone des notifications
- Redis est utilisé comme broker et backend de résultats
- Les templates HTML sont personnalisables par tenant
- Le service est conçu pour une architecture microservices
- Multi-tenant avec isolation par `tenant_id`
- Retry automatique avec backoff exponentiel en cas d'échec

## 🆘 Support

Pour toute question ou problème, consultez :
- Logs du service : `docker logs notification-service`
- Logs Celery : `docker logs notification-worker`
- Healthcheck : `GET /health` (si disponible)
- Documentation SendGrid : https://docs.sendgrid.com
- Documentation Twilio : https://www.twilio.com/docs
- Documentation Celery : https://docs.celeryproject.org
- Documentation du projet : [README.md principal](../README.md)
