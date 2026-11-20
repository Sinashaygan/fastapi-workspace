from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    JWT_SECRET_KEY: str = "test"
    REDIS_URL: str

    MAIL_USERNAME: str = ""  # اصلاح شده (بدون پرانتز و کاما)
    MAIL_PASSWORD: str = ""  # اصلاح شده
    MAIL_FROM: str = "from@example.com"  # اصلاح شده
    MAIL_PORT: int = 25  # پورت داکر برای smtp4dev (یا 25)
    MAIL_SERVER: str = "smtp4dev"  # اصلاح شده
    MAIL_FROM_NAME: str = "FastAPI Mailer"  # اصلاح شده
    MAIL_STARTTLS: bool = False  # اصلاح شده
    MAIL_SSL_TLS: bool = False  # اصلاح شده
    USE_CREDENTIALS: bool = False
    CELERY_BROKER_URL:str = "redis://redis:6379/3"
    CELERY_BACKEND_URL:str = "redis://redis:6379/3"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
