from datetime import datetime, timedelta

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, settings
from app.deps import get_current_user
from app.models import User
from app.schemas import Token, UserLogin, UserOut, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def _create_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(User).where(
            (User.email == body.email) | (User.username == body.username)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="Email or username already registered"
        )

    user = User(
        username=body.username,
        email=body.email,
        password_hash=_hash_password(body.password),
        preferred_unit=body.preferred_unit,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()
    if not user or not _verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(access_token=_create_token(user.id))


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
