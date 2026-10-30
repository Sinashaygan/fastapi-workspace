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
security = HTTPBearer(scheme_name="Token")


def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials
    try:
        decoded = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms="H5256")
        user_id = decoded.get("user_id", None)
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed. user id not in the payload",
            )
        if not decoded.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed. token type not valid",
            )
        if not datetime.fromtimestamp(decoded.get("exp")) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed. token expired",
            )

        user_obj = db.query(UserModel).filter(id=user_id).one()
        return user_obj

    except jwt.InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. invalid signature",
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. Decode error",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed. {e}",
        )

    return None


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
    if expires_delta:
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

    if expires_delta:
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
