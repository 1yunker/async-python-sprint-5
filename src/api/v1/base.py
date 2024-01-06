import logging
from datetime import datetime

from aioredis import Redis
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_cache.decorator import cache
from fastapi_login.exceptions import InvalidCredentialsException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.config import app_settings
from core.logger import LOGGING
from db.db import get_session
from schemas.file import FileResponse, UserFilesResponse
from schemas.ping import Ping
from schemas.user import UserCreate, UserResponse
from services.file import download_file, file_crud, upload_file
from services.security import manager, verify_password
from services.user import create_user, get_user

router = APIRouter()

logging.basicConfig = LOGGING
logger = logging.getLogger()


@router.post(
    app_settings.register_url,
    status_code=status.HTTP_201_CREATED,
    description='Регистрация пользователя.')
async def register(user: UserCreate,
                   db: AsyncSession = Depends(get_session)):
    db_user = await get_user(user.email, db)
    if db_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='A user with this email already exists'
        )
    else:
        db_user = await create_user(db, user)
        return UserResponse(id=db_user.id, email=db_user.email)


@router.post(
    app_settings.token_url,
    description='Авторизация пользователя и получение токена.')
async def login(
        data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_session)
):
    user = await get_user(email=data.username, db=db)
    if user is None:
        raise InvalidCredentialsException
    elif not verify_password(data.password, user.hashed_password):
        raise InvalidCredentialsException

    access_token = manager.create_access_token(
        data=dict(sub=user.email)
    )
    return {'access_token': access_token, 'token_type': 'Bearer'}


@router.get(
    '/ping',
    response_model=Ping,
    status_code=status.HTTP_200_OK,
    description='Информация о времени доступа к связанным сервисам.')
async def get_ping(db: AsyncSession = Depends(get_session)):
    # Test connection to DB
    try:
        start_db = datetime.utcnow()
        await db.scalar(select(1))
        time_db = (datetime.utcnow() - start_db).total_seconds()
        logger.info('Send ping to DB.')
    except Exception:
        time_db = 'Disconnected'
        logger.warning('DB disconnected')

    # Test connection to Redis
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

    return Ping(db=time_db, cache=time_redis)


@router.get(
    '/files',
    response_model=UserFilesResponse,
    description='Информация о загруженных файлах текущего пользователя.')
@cache(expire=30)
async def get_files_info(
        db: AsyncSession = Depends(get_session),
        user=Depends(manager)
):
    list_file_obj = await file_crud.get_multi_by_user_id(
        db=db,
        user_id=user.id
    )
    return UserFilesResponse(account_id=user.id, files=list_file_obj)


@router.post(
    '/files/upload',
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
    description='Загрузить файл.'
)
async def upload_file_by_path(
        file: UploadFile,
        path: str = '',
        db: AsyncSession = Depends(get_session),
        user=Depends(manager)
):
    return await upload_file(file, path, db, user)


@router.get(
    '/files/download',
    status_code=status.HTTP_200_OK,
    description='Скачать файл по переданному пути или по идентификатору.'
)
@cache(expire=60)
async def download_file_by_path_or_id(
        path: str,
        db: AsyncSession = Depends(get_session),
        user=Depends(manager)
):
    return await download_file(path, db, user)
