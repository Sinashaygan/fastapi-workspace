from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# Email Configuration for smtp4dev inside Docker Compose
conf = ConnectionConfig(
    
)

# Function to send an email
async def send_email(subject: str, recipients: list[str], body: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype="plain"
    )

    fm = FastMail(conf)
    await fm.send_message(message)
