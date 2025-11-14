import os
import resend
from jinja2 import Environment, FileSystemLoader
from src.config import settings

resend.api_key = settings.RESEND_API_KEY

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "../templates/email")
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


async def send_email(subject: str, recipient: str, html_content: str):
    print(f"Sending email to {recipient} | Subject: {subject}")
    try:
        response = resend.Emails.send({
            "from": f"Nibra Al-Deen <{settings.EMAIL_FROM}>",
            "to": [recipient],
            "subject": subject,
            "html": html_content,
        })
        print("Resend API response:")
        print(response)
        return response
    except Exception as e:
        print("Error sending email:")
        print(e)
        raise


async def send_password_reset_email(email: str, code: str):
    template = env.get_template("password_reset.html")
    html_content = template.render(code=code)
    subject = "Your Password Reset Code"
    await send_email(subject, email, html_content)


async def send_contact_notification(message_data, recipient: str = "ajisafeibrahim54@gmail.com"):
    template = env.get_template("contact_notification.html")
    html_content = template.render(
        name=message_data.name,
        email=message_data.email,
        subject=message_data.subject,
        message=message_data.message
    )
    await send_email(f"New Contact Message: {message_data.subject}", recipient, html_content)
