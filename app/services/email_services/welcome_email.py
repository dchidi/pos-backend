from email.message import EmailMessage
from aiosmtplib import SMTP

from app.core.settings import settings 

from app.utils.template_path import template_env


async def send_welcome_email(to_email: str, verification_url: str):
    msg = EmailMessage()
    msg["Subject"] = f"{settings.APP_NAME} New User Account Verification"
    msg["From"] = settings.FROM_EMAIL
    msg["To"] = to_email


     # Render HTML with Jinja2
    template = template_env.get_template("welcome_email.html")
    html_content = template.render(
        verification_url=verification_url, 
        app_name=settings.APP_NAME, 
        expiry_time=settings.ACCOUNT_VERIFICATION_EXPIRY_TIME_HOURS
    )
    msg.add_alternative(html_content, subtype="html")

    try:
        smtp = SMTP(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            use_tls=True
        )
        await smtp.connect()
        await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        await smtp.send_message(msg)
        await smtp.quit()
    except Exception as e:
        print(f"[Email Error] Failed to send OTP to {to_email}: {e}")
        raise RuntimeError("Failed to send verification email")
