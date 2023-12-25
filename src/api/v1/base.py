import logging
from datetime import datetime

from aioredis import Redis
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from sqlalchemy.future import select

from core.config import app_settings
from core.logger import LOGGING
from db.db import get_session
from schemas.ping import Ping
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


@router.get('/private')
def private_route(user=Depends(manager)):
    return {"detail": f"Welcome {user.email}"}


@router.get('/ping', response_model=Ping, status_code=status.HTTP_200_OK)
async def get_ping(db=Depends(get_session)):
    """
    Информация о времени доступа к связанным сервисам.
    """
    try:
        start_db = datetime.utcnow()
        await db.scalar(select(1))
        time_db = (datetime.utcnow() - start_db).total_seconds()
        logger.info('Send ping to DB.')
    except Exception:
        time_db = 'Disconnected'
        logger.warning('DB disconnected')

    try:
        start_redis = datetime.utcnow()
        redis_connection = Redis(
            host=app_settings.redis_host,
            port=app_settings.redis_port,
            decode_responses=True
        )
        await redis_connection.ping()
        time_redis = (datetime.utcnow() - start_redis).total_seconds()
        logger.info('Send ping to Redis.')
    except Exception:
        time_redis = 'Disconnected'
        logger.warning('Redis disconnected')

    return {
        'db': time_db,
        'cache': time_redis
    }
