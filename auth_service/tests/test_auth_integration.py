import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.db.base import Base
from app.main import app


@pytest.fixture
async def test_client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_db():
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_register_login_me_flow(test_client: AsyncClient):
    register_resp = await test_client.post(
        "/auth/register",
        json={"email": "surname@email.com", "password": "secret123"},
    )
    assert register_resp.status_code == 201

    login_resp = await test_client.post(
        "/auth/login",
        data={"username": "surname@email.com", "password": "secret123"},
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    me_resp = await test_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "surname@email.com"


@pytest.mark.asyncio
async def test_duplicate_registration_returns_409(test_client: AsyncClient):
    await test_client.post(
        "/auth/register",
        json={"email": "surname@email.com", "password": "secret123"},
    )

    resp = await test_client.post(
        "/auth/register",
        json={"email": "surname@email.com", "password": "secret123"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(test_client: AsyncClient):
    await test_client.post(
        "/auth/register",
        json={"email": "surname@email.com", "password": "secret123"},
    )

    resp = await test_client.post(
        "/auth/login",
        data={"username": "surname@email.com", "password": "wrong"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_without_token_returns_401(test_client: AsyncClient):
    resp = await test_client.get("/auth/me")
    assert resp.status_code == 401