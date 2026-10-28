

from datetime import datetime, timedelta, timezone

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from requests import Session

from core.database import get_db

SECRET_KEY = "your-very-secure-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
security = HTTPBearer(scheme_name="Token")

def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
        
    return 


def generate_access_token(user_id: int | str, payload: dict | None = None, expires_delta: timedelta | None = None) -> str:
    """
    تولید Access Token با pyjwt
    - user_id: شناسه کاربر که در کلید sub (Subject) ذخیره می‌شود
    - payload: داده‌های اختیاری اضافی که می‌خواهید درون توکن قرار گیرد
    - expires_delta: مدت زمان دلخواه انقضا (در صورت عدم ارسال، پیش‌فرض اعمال می‌شود)
    """
    # ایجاد یک کپی از داده‌های ورودی یا یک دیکشنری خالی
    to_encode = payload.copy() if payload else {}

    now = datetime.now(timezone.utc)
    
    # تعیین زمان انقضا
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # افزودن ادعاها (Claims) استاندارد JWT:
    # sub: شناسه کاربر
    # iat: زمان صدور (Issued At)
    # exp: زمان انقضا (Expiration Time)
    to_encode.update({
        "sub": str(user_id),
        "user_id": user_id,  # اضافه کردن صریح user_id در صورت نیاز
        "iat": now,
        "exp": expire,
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt