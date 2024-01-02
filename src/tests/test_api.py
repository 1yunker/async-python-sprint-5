import pytest
import pytest_asyncio

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import app_settings
from db.db import get_session
from main import app
from models import Base

TEST_DATABASE_DSN = 'sqlite+aiosqlite:///./src/tests/test.db'

client = TestClient(app=app)


def get_engine():
    return create_async_engine(
        TEST_DATABASE_DSN,
        echo=app_settings.echo | True,
        future=True
    )


async def override_get_session() -> AsyncSession:
    engine = get_engine()
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session


@pytest_asyncio.fixture(scope='module')
async def prepare_db():
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.mark.usefixtures('prepare_db')
def test_register():
    response = client.post(
        app.url_path_for('register'),
        json={'email': 'user@example.com', 'password': 'string'}
    )
    assert response.status_code == 201
    assert response.json() == {'id': 1, 'email': 'user@example.com'}


def test_login(cache):
    response = client.post(
        app.url_path_for('login'),
        data={'username': 'user@example.com', 'password': 'string'},
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    cache.set('access_token', response.json().get('access_token'))

    assert response.status_code == 200


def test_get_ping():
    response = client.get(
        app.url_path_for('get_ping')
    )
    assert response.status_code == 200


@pytest.mark.dependency(depends=['test_login'])
def test_get_files_info(cache):
    token = cache.get('access_token', None)
    response = client.get(
        app.url_path_for('get_files_info'),
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == 200
    assert response.json() == {'account_id': 1, 'files': []}
