from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from core.config import settings

# Email Configuration for smtp4dev inside Docker Compose
conf = ConnectionConfig(
    settings.MAIL_USERNAME,
    settings.MAIL_PASSWORD,
    settings.MAIL_FROM,
    settings.MAIL_PORT,
    settings.MAIL_SERVER,
    settings.MAIL_FROM_NAME,
    settings.MAIL_STARTTLS,
    settings.MAIL_SSL_TLS,
    settings.USE_CREDENTIALS,
)


# Function to send an email
async def send_email(subject: str, recipients: list[str], body: str):
    message = MessageSchema(
        subject=subject, recipients=recipients, body=body, subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
