from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    JWT_SECRET_KEY: str = "test"
    REDIS_URL: str

    MAIL_USERNAME: str = ("",)  # در smtp4dev نیازی به یوزرنام نیست
    MAIL_PASSWORD: str = ("",)  # در smtp4dev نیازی به پسورد نیست
    MAIL_FROM: str = ("from@example.com",)  # ایمیل فرستنده نمایشی
    MAIL_PORT: int = (25,)  # پورت ۲۵ برای smtp4dev
    MAIL_SERVER: str = ("smtp4dev",)  # نام سرویس در داکر کامپوز
    MAIL_FROM_NAME: str = ("FastAPI Mailer",)
    MAIL_STARTTLS: bool = (False,)  # در smtp4dev نیازی به TLS نیست
    MAIL_SSL_TLS: bool = (False,)  # در smtp4dev نیازی به SSL نیست
    USE_CREDENTIALS: bool = False  # چون احراز هویت ندارد False می‌شود

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
