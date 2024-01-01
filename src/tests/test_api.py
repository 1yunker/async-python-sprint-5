from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import app_settings
from db.db import get_session
from main import app
from models import Base

client = TestClient(app=app)


async def override_get_session() -> AsyncSession:
    engine = create_async_engine(
        str(app_settings.database_dsn),
        echo=app_settings.echo | True,
        future=True
    )

    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session

app.dependency_overrides[get_session] = override_get_session


def test_register():
    response = client.post(
        app.url_path_for('register'),
        json={'email': 'user@example.com', 'password': 'string'}
    )
    assert response.status_code == 201
    assert response.json() == {'id': 1, 'email': 'user@example.com'}


def test_login_and_get_files_info():
    response = client.post(
        app.url_path_for('login'),
        data={'username': 'user@example.com', 'password': 'string'},
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    assert response.status_code == 200
    token = response.json().get('access_token')

    response = client.get(
        app.url_path_for('get_files_info'),
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    assert response.json() == {'account_id': 1, 'files': []}


def test_get_ping():
    response = client.get(
        app.url_path_for('get_ping')
    )
    assert response.status_code == 200
