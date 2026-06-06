import pytest
from httpx import AsyncClient
from app.main import app
from app.database import Base, engine, SessionLocal
import os

# 테스트용 DB 설정 (메모리 내 SQLite 등 고려 가능하나, 여기서는 편의상 동일 설정 혹은 별도 환경 권장)
# MVP 단계에서는 실제 DB 연결 테스트로 진행

@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"

@pytest.mark.anyio
async def test_signup():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "username": "testuser",
                "password": "testpassword",
                "age_group": "20s",
                "occupation": "developer"
            }
        )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

@pytest.mark.anyio
async def test_login():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpassword"
            }
        )
    assert response.status_code == 200
    assert "access_token" in response.json()
