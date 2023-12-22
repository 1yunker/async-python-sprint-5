from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import app_settings


async def get_session() -> AsyncSession:
    async with db_session() as session:
        yield session

engine = create_async_engine(
    str(app_settings.database_dsn),
    echo=app_settings.echo | False,
    future=True
)
db_session = sessionmaker(
    engine, class_=AsyncSession,
    expire_on_commit=False
)


class DBContext:

    def __init__(self):
        self.db = db_session()

    def __enter__(self):
        return self.db

    def __exit__(self, exc_type, exc_value, traceback):
        self.db.close()


def get_db() -> AsyncSession:
    """
    Returns the current db connection.
    """
    with DBContext() as db:
        yield db
