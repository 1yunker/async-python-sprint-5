import logging

import boto3
from fastapi import HTTPException, status

from core.config import app_settings
from core.logger import LOGGING

logging.basicConfig = LOGGING
logger = logging.getLogger()


def get_s3_client():
    session = boto3.session.Session()
    try:
        return session.client(
            service_name=app_settings.s3_service_name,
            endpoint_url=app_settings.s3_endpoint_url,
            aws_access_key_id=app_settings.aws_access_key_id,
            aws_secret_access_key=app_settings.aws_secret_access_key,
        )
    except Exception as err:
        logger.error(err)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Error: {err}'
        )
