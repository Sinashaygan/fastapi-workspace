from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from users.shemas import *
from users.models import UserModel
from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter(tags=["users"], prefix="/users")

@router.post("/login")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    return {}

@router.post("/register")
async def user_register(request: UserRegisterSchema, db: Session = Depends(get_db)):
    return {}