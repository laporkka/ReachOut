import uuid
import pytest
import httpx
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from reachout.src.core.config import settings 
from reachout.src.core.database import get_db
from reachout.src.models import Base
from reachout.src .main import app
from reachout.src.tasks.celery_app import celery_app
from reachout.src.models.user import Manager
from reachout.src.services.auth import AuthService


test_engine = create_async_engine(settings.TEST_ASYNC_POSTGRES_URL, echo=True)
test_AsyncSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def db_engine():
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True 

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    celery_app.conf.task_always_eager = False
    celery_app.conf.task_eager_propagates = False 


@pytest.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async with test_AsyncSessionLocal() as session:
        yield session

        await session.rollback()

"""
@pytest.fixture(scope="function")
async def registered_manager(db_session: AsyncSession) -> Manager:
    manager = await AuthService(db_session)
    
    db_session.commit()

    yield manager
"""

@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[httpx.AsyncClient, None]:
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test"
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def register_manager(client):
    unique_email = f"test{uuid.uuid4().hex[:6]}@test.com"
    request = {
        "email": unique_email,
        "password": "testpassword"
    }

    response = await client.post("/managers/register", json=request)

    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["email"] == request["email"]

    return request


@pytest.fixture(scope="function")
async def login_manager_header(client, register_manager):
    request = {
        "username": register_manager["email"],
        "password": register_manager["password"]
    }

    response = await client.post("/managers/login", data=request)

    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    return headers
    
"""
@pytest.fixture(scope="function")
async def register_specific_manager(client):
    request = {
        "email": "specificmanager@test.com",
        "password": "testpassword"
    }

    response = await client.post("/managers/register", json=request)

    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["email"] == request["email"]

    return request


@pytest.fixture(scope="function")
async def login_specific_manager(client, register_specific_manager):
    request = {
        "username": register_specific_manager["email"],
        "password": register_specific_manager["password"]
    }

    response = await client.post("/managers/login", data=request)

    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    client.headers.update(headers)
"""

@pytest.fixture(scope="function")
async def add_campaign(client: httpx.AsyncClient, login_manager_header):
    request = {
        "items": [
            {
                "first_name": "testvipclient",
                "email": "testvipclient@test.com",
                "birthday": "5751-67-61",
                "tags": [
                    "VIP"
                ]
            }
        ]
    }
