from datetime import timedelta

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env.example')

    app_title: str = 'Default_title'
    echo: bool = True

    postgres_db: str = 'postgres'
    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres'

    postgres_host: str = 'localhost'
    postgres_port: int = 5432
    database_dsn: PostgresDsn | None = None

    project_host: str = '127.0.0.1'
    project_port: int = 8000

    redis_host: str = '127.0.0.1'
    redis_port: int = 6379

    secret: str = 'your-secret-key'
    register_url: str = '/register'
    token_url: str = '/auth'
    token_expires: timedelta = timedelta(minutes=30)

    s3_service_name: str = 's3'
    s3_endpoint_url: str = 'https://storage.yandexcloud.net'
    aws_access_key_id: str = 'YOUR_KEY'
    aws_secret_access_key: str = 'YOUR_SECRET'
    bucket: str = 'YOUR_BUCKET'

    local_download_dir: str = '/app/downloads'


app_settings = AppSettings()
