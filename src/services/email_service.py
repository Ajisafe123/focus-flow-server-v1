import os
import asyncio
from datetime import datetime
from email.message import EmailMessage

import aiosmtplib
from jinja2 import Environment, FileSystemLoader
from src.config import settings

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../templates/email")
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


async def send_email(subject: str, recipient: str, html_content: str):
    """Send an email using Brevo SMTP."""
    print(f"Sending email to {recipient} | Subject: {subject}")
    message = EmailMessage()
    message["From"] = f"Nibra Al-Deen <{settings.EMAIL_FROM}>"
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content("Your email client does not support HTML.")
    message.add_alternative(html_content, subtype="html")

    async def _send():
        async with aiosmtplib.SMTP(
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            start_tls=True,
            timeout=60,
        ) as smtp:
            print(f"SMTP: Connected to {settings.SMTP_HOST}:{settings.SMTP_PORT}. Logging in...")
            await smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            print("SMTP: sending message...")
            response = await smtp.send_message(message)
            print(f"SMTP: send completely successful to {recipient}")
            return response

    try:
        # Hard cap total send time to 120s
        response = await asyncio.wait_for(_send(), timeout=120)
        print("Brevo SMTP response:")
        print(response)
        return response
    except Exception as e:
        import traceback
        print(f"❌ FAILED sending email to {recipient}")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("Full Traceback:")
        traceback.print_exc()
        raise


async def send_password_reset_email(email: str, code: str):
    template = env.get_template("password_reset.html")
    html_content = template.render(code=code)
    subject = "Your Password Reset Code"
    await send_email(subject, email, html_content)


async def send_contact_notification(message_data, recipient: str = settings.EMAIL_FROM):
    template = env.get_template("contact_notification.html")
    html_content = template.render(
        name=message_data.name,
        email=message_data.email,
        subject=message_data.subject,
        message=message_data.message
    )
    await send_email(
        f"New Contact Message: {message_data.subject}",
        recipient or settings.EMAIL_FROM,
        html_content,
    )


async def send_login_notification(email: str):
    """Send a brief login notice to the user."""
    html_content = f"""
    <div style="font-family: Arial, sans-serif; padding: 16px;">
      <h2>Login Notification</h2>
      <p>We noticed a new sign-in to your Nibras Al-Deen account.</p>
      <p>If this was you, no action is needed. If not, please reset your password.</p>
      <p style="color: #0f5132;">Time: {datetime.utcnow().isoformat()} UTC</p>
    </div>
    """
    await send_email("You just signed in", email, html_content)