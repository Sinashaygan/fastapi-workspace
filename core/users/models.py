from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func
from core.database import Base
from sqlalchemy.orm import relationship
from passlib.context import CryptContext

# راه‌اندازی تنظیمات هشینگ با استفاده از الگوریتم bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(250), nullable=False)
    password = Column(String, nullable=False)
    is_active= Column(Boolean, default=True)

    created_date = Column(DateTime, server_default=func.now())
    updated_date = Column(DateTime, server_default=func.now(), onupdate=func.now())

    tasks = relationship("TaskModel" , back_populates="user")

    def hash_password(password: str) -> str:
        """پسورد متنی را دریافت کرده و نسخه هش‌شده آن را برمی‌گرداند."""
        return pwd_context.hash(password)


    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """پسورد وارد شده توسط کاربر را با پسورد هش‌شده داخل دیتابیس مقایسه می‌کند."""
        return pwd_context.verify(plain_password, hashed_password)

    def set_password(self,plain_text:str)->None:
        self.password = self.hash_password(plain_text)
