import logging
import os

from aiofiles.os import makedirs
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse as FastapiFileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import app_settings
from core.logger import LOGGING
from db.db import get_session
from models.models import File as FileModel
from schemas.file import FileUpload
from services.boto3 import get_s3_client
from services.security import manager

from .base import RepositoryDB


class RepositoryFile(RepositoryDB[FileModel, FileUpload, FileUpload]):
    pass


file_crud = RepositoryFile(FileModel)

logging.basicConfig = LOGGING
logger = logging.getLogger()


def get_file_params(file: UploadFile, prefix_path: str = '', path: str = ''):
    """
    Prepare "file_name" and "path" params.
    """
    file_name = file.filename
    if not path:
        path = prefix_path + file_name
    elif path[-1] == '/':
        # path: <path-to-folder>
        path = prefix_path + path + file_name
    else:
        # path: <full-path-to-file>
        file_name = os.path.split(path)[-1]
        path = prefix_path + path
    return file_name, path


async def upload_file(
        file: UploadFile,
        path: str = '',
        db: AsyncSession = Depends(get_session),
        user=Depends(manager)
):
    # Prepare "file_name" and "path" params
    file_name, path = get_file_params(file, f'{user.email}/', path)

    # Write file in DB
    try:
        file_obj = await file_crud.create(
            db=db,
            obj_in=FileUpload(user_id=user.id,
                              path=path,
                              name=file_name,
                              size=file.size)
        )
    except Exception as err:
        logger.error(f'{err}')
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Error: {err}'
        )

    # Upload file in S3 storage
    s3 = get_s3_client()
    async with s3:
        try:
            await s3._client.upload_fileobj(
                file.file, app_settings.bucket, path
            )
            logger.info(f'Upload file {path} from {user.email}')
        except Exception as err:
            logger.error(f'{err}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Something went wrong'
            )

    return file_obj


async def download_file(
        path: str,
        db: AsyncSession = Depends(get_session),
        user=Depends(manager)
):
    # Get file_obj from DB
    if path.isnumeric():
        file_obj = await file_crud.get(db=db, id=int(path))
    else:
        file_obj = await file_crud.get_by_path(db=db, path=path)

    if file_obj:
        if file_obj.is_downloadable:
            # Create dirs by full_local_path
            full_local_path = '/'.join(
                [app_settings.local_download_dir, user.email]
            )
            await makedirs(full_local_path, exist_ok=True)

            # Download file from S3 storage
            s3 = get_s3_client()
            full_local_path_to_file = '/'.join(
                [full_local_path, file_obj.name]
            )
            async with s3:
                await s3._client.download_file(
                    app_settings.bucket,
                    file_obj.path,
                    full_local_path_to_file
                )
                return FastapiFileResponse(
                    path=full_local_path_to_file,
                    media_type='application/octet-stream',
                    filename=file_obj.name
                )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='File is not downloadable'
        )
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='File not found'
    )
