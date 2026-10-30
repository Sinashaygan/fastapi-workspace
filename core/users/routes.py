import secrets
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse
from auth.jwt_auth import decode_refresh_token, generate_access_token, generate_refresh_token
from users.schemas import *
from users.models import TokenModel, UserModel
from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter(tags=["users"], prefix="/users")


def generate_random_token(length: int = 32) -> str:
    """
    تولید یک توکن امن تصادفی (Base64 URL-safe)
    خروجی به صورت رشته‌ای از کاراکترها بدون نیاز به هیچ پکیج اضافی است.
    """
    return secrets.token_urlsafe(length)


@router.post("/login")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    user_obj = db.query(UserModel).filter_by(username=request.username).first()
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="username does not exist."
        )
    if not user_obj.verify_password(request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="password is invalid"
        )

    # token_obj = TokenModel(userId=user_obj.id, token=generate_random_token())
    # db.add(token_obj)
    # db.commit()
    # db.refresh(token_obj)

    access_token = generate_access_token(user_obj.id)
    refresh_token = generate_refresh_token(user_obj.id)

    return JSONResponse(
        content={
            "detail": "logged in successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )


@router.post("/register")
async def user_register(request: UserRegisterSchema, db: Session = Depends(get_db)):
    if db.query(UserModel).filter_by(username=request.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="username already exist."
        )
    user_obj = UserModel(username=request.username.lower())
    user_obj.set_password(request.password)
    db.add(user_obj)
    db.commit()
    db.refresh()
    return JSONResponse(content={"detail": "user registered successfully"})


@router.post("/refresh-token")
async def user_refresh_token(request: UserRefreshTokenSchema, db: Session = Depends(get_db)):
    user_id = decode_refresh_token(request.refresh_token)
    access_token = generate_access_token(user_id)

    return JSONResponse(content={"access_token": access_token})
