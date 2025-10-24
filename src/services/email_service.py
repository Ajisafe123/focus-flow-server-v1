import aiosmtplib
from email.message import EmailMessage
from jinja2 import Environment, FileSystemLoader
import os
import asyncio
from ..config import settings

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../templates/email")
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))

async def send_email(subject: str, recipient: str, html_content: str):
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content("This email requires HTML support.")
    msg.add_alternative(html_content, subtype="html")

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        start_tls=True,
    )

async def send_password_reset_email(email: str, code: str):
    template = env.get_template("password_reset.html")
    html_content = template.render(code=code)
    subject = "Your Password Reset Code"
    await send_email(subject, email, html_content)
