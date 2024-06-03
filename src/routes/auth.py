import logging
import select
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, Security
from fastapi.security import (
    HTTPAuthorizationCredentials,
    OAuth2PasswordRequestForm,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
# from src.entity.models import Todo
from src.repositories import users as repositories_users
from src.schemas.user import UserSchema, UserResponse, TokenSchema
from src.services.auth import auth_service


router = APIRouter(prefix="/auth", tags=["auth"])

get_refresh_token = HTTPBearer()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.post(
    "/signup",
    response_model=Optional[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def signup(body: UserSchema, db: AsyncSession = Depends(get_db)):
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.add_user(body, db)
    # print()
    # new_user = User(
    #     email=body.username, password=hash_handler.get_password_hash(body.password)
    # )

    return new_user


@router.post("/login", response_model=Optional[TokenSchema])
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await repositories_users.get_user_by_email(body.username, db)
    # user = db.query(User).filter(User.email == body.username).first()
    if user is None:
        logger.error("User not found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not auth_service.verify_password(body.password, user.password):
        logger.error("password incorrect")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh_token", response_model=Optional[TokenSchema])
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
    db: AsyncSession = Depends(get_db),
):
    print(credentials.credentials)
    print("#############")
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repositories_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
