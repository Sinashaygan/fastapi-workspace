from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session
from core.config import settings
from core.database import get_db
from users.models import UserModel

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 5
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24
security = HTTPBearer(scheme_name="Token", auto_error=False)


def authentication_error(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> UserModel:
    if credentials is None:
        raise authentication_error("Not authenticated")

    token = credentials.credentials
    try:
        # PyJWT verifies the signature and expiration; exp must also be present.
        decoded = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require": ["exp"]},
        )
    except jwt.ExpiredSignatureError:
        raise authentication_error("Authentication failed. token expired")
    except jwt.InvalidSignatureError:
        raise authentication_error("Authentication failed. invalid signature")
    except jwt.DecodeError:
        raise authentication_error("Authentication failed. Decode error")
    except jwt.InvalidTokenError:
        raise authentication_error("Authentication failed. invalid token")

    user_id = decoded.get("user_id")
    if not user_id:
        raise authentication_error("Authentication failed. user id not in the payload")

    if decoded.get("type") != "access":
        raise authentication_error("Authentication failed. token type not valid")

    user_obj = db.query(UserModel).filter_by(id=user_id).one_or_none()
    if user_obj is None:
        raise authentication_error("User not found")
    return user_obj


def generate_access_token(
    user_id: int | str,
    payload: dict | None = None,
    expires_delta: timedelta | None = None,
) -> str:
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
    if expires_delta is not None:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # افزودن ادعاها (Claims) استاندارد JWT:
    # sub: شناسه کاربر
    # iat: زمان صدور (Issued At)
    # exp: زمان انقضا (Expiration Time)
    to_encode.update(
        {
            "type": "access",
            "sub": str(user_id),
            "user_id": user_id,  # اضافه کردن صریح user_id در صورت نیاز
            "iat": now,
            "exp": expire,
        }
    )

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_refresh_token(
    user_id: int | str, expires_delta: timedelta | None = None
) -> str:
    """
    تولید Refresh Token با pyjwt
    - user_id: شناسه کاربر
    - expires_delta: مدت زمان دلخواه انقضا (در صورت عدم ارسال، پیش‌فرض ۲۴ ساعت اعمال می‌شود)
    """
    now = datetime.now(timezone.utc)

    if expires_delta is not None:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "type": "refresh",  # نوع توکن برای جلوگیری از سوءاستفاده به عنوان access token
        "sub": str(user_id),
        "user_id": user_id,
        "iat": now,
        "exp": expire,
    }

    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
