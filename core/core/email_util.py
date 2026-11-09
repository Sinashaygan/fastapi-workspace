from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

# Email Configuration for smtp4dev inside Docker Compose
conf = ConnectionConfig(
    MAIL_USERNAME="",                  # در smtp4dev نیازی به یوزرنام نیست
    MAIL_PASSWORD="",                  # در smtp4dev نیازی به پسورد نیست
    MAIL_FROM="from@example.com",       # ایمیل فرستنده نمایشی
    MAIL_PORT=25,                      # پورت ۲۵ برای smtp4dev
    MAIL_SERVER="smtp4dev",            # نام سرویس در داکر کامپوز
    MAIL_FROM_NAME="FastAPI Mailer",
    MAIL_STARTTLS=False,               # در smtp4dev نیازی به TLS نیست
    MAIL_SSL_TLS=False,                # در smtp4dev نیازی به SSL نیست
    USE_CREDENTIALS=False              # چون احراز هویت ندارد False می‌شود
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
