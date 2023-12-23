import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException

from core.logger import LOGGING
from core.config import app_settings
from db.db import get_session
from schemas.user import UserCreate, UserResponse
from services.security import manager, verify_password
from services.user import create_user, get_user

router = APIRouter()

logging.basicConfig = LOGGING
logger = logging.getLogger()


@router.post(app_settings.register_url)
async def register(user: UserCreate, db=Depends(get_session)):
    """
    Регистрация пользователя.
    """
    db_user = await get_user(user.email, db)
    if db_user is not None:
        raise HTTPException(status_code=400,
                            detail="A user with this email already exists")
    else:
        db_user = await create_user(db, user)
        return UserResponse(id=db_user.id, email=db_user.email)


@router.post(app_settings.token_url)
async def login(data: OAuth2PasswordRequestForm = Depends(),
                db=Depends(get_session)):
    """
    Авторизация пользователя.
    """
    email = data.username
    password = data.password

    user = await get_user(email, db)
    if user is None:
        raise InvalidCredentialsException
    elif not verify_password(password, user.hashed_password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data=dict(sub=user.email)
    )
    return {'access_token': access_token, 'token_type': 'Bearer'}
