from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env.example')

    app_title: str = 'Default_title'

    database_dsn: PostgresDsn | None = None
    echo: bool = True

    project_host: str = '127.0.0.1'
    project_port: int = 8000


app_settings = AppSettings()
