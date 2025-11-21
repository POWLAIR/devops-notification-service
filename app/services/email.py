from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from jinja2 import Environment, FileSystemLoader
import os
import logging

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        api_key = os.getenv('SENDGRID_API_KEY')
        if not api_key:
            logger.warning("⚠️ SENDGRID_API_KEY not configured")
            self.sg = None
        else:
            self.sg = SendGridAPIClient(api_key)
        
        # Charger le template engine
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.template_env = Environment(loader=FileSystemLoader(template_dir))
    
    def send_order_confirmation(self, to_email: str, order_data: dict, tenant_settings: dict) -> bool:
        """Envoyer email de confirmation de commande"""
        try:
            # Render template
            template = self.template_env.get_template('order_confirmation.html')
            html_content = template.render(
                order=order_data,
                tenant=tenant_settings
            )
            
            # Create message
            from_email = tenant_settings.get('email_from', os.getenv('SENDGRID_FROM_EMAIL', 'noreply@saas-platform.com'))
            subject = f"Confirmation de commande #{order_data.get('orderNumber', 'N/A')}"
            
            message = Mail(
                from_email=Email(from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            # Send
            if self.sg:
                response = self.sg.send(message)
                logger.info(f"✅ Email sent to {to_email} - Status: {response.status_code}")
                return response.status_code == 202
            else:
                logger.warning(f"⚠️ Email simulation (SendGrid not configured): {to_email}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error sending email: {e}")
            raise
    
    def send_welcome_email(self, to_email: str, user_data: dict, tenant_settings: dict) -> bool:
        """Envoyer email de bienvenue"""
        try:
            template = self.template_env.get_template('welcome.html')
            html_content = template.render(
                user=user_data,
                tenant=tenant_settings
            )
            
            from_email = tenant_settings.get('email_from', os.getenv('SENDGRID_FROM_EMAIL', 'noreply@saas-platform.com'))
            subject = f"Bienvenue sur {tenant_settings.get('name', 'notre plateforme')} !"
            
            message = Mail(
                from_email=Email(from_email),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )
            
            if self.sg:
                response = self.sg.send(message)
                logger.info(f"✅ Welcome email sent to {to_email}")
                return response.status_code == 202
            else:
                logger.warning(f"⚠️ Email simulation: {to_email}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error sending welcome email: {e}")
            raise



