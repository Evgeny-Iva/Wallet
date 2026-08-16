import pytest
import uuid

from api.tests.conftest import test_user


@pytest.mark.asyncio
async def test_register_success(client):
    """Проверяет создание нового пользователя"""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "secret123"
    }
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User created"
    assert "user_id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client, test_user):
    """Проверяет повторное создания пользователя по одному email"""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test_duplicate@example.com",
        "password": "secret123"
    }
    response_first = await client.post("/auth/register", json=user_data)
    assert response_first.status_code == 200

    response_second = await client.post("/auth/register", json=user_data)
    assert response_second.status_code == 400
    assert response_second.json()["detail"] == "Email already registered"


@pytest.mark.asyncio
async def test_login_success(client, test_user):
    """Логин с верным паролем"""
    login_data = {"email": test_user["email"], "password": test_user["password"]}
    login_response = await client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"] != ""


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    """Тест авторизации с не правильным паролем"""
    login_data = {"email": test_user["email"], "password": "password"}
    login_response = await client.post("/auth/login", json=login_data)
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Unauthorized"


@pytest.mark.asyncio
async def test_login_user_not_found(client):
    """Тест на не существующего пользователя"""
    login_data = {"email": "test@example.com", "password": "secret123"}
    login_response = await client.post("/auth/login", json=login_data)
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Unauthorized"


@pytest.mark.asyncio
async def test_me_unauthorized(client):
    """Тест на проверку получения данных будучи не авторизованным"""
    response = await client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_me_success(client, test_user):
    """Тест на получение данных авторизованным пользователем"""
    login_data = {"email": test_user["email"], "password": test_user["password"]}
    login_response = await client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_response = await client.get("/users/me", headers=headers)
    assert me_response.status_code == 200

    me_data = me_response.json()
    assert me_data["email"] == test_user["email"]
    assert me_data["first_name"] == test_user["first_name"]
    assert me_data["last_name"] == test_user["last_name"]
    assert "id" in me_data
    assert "created_at" in me_data


@pytest.mark.asyncio
async def test_logout_success(client, test_user):
    """Тест на выход из профиля"""
    login_data = {"email": test_user["email"], "password": test_user["password"]}
    login_response = await client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

    data = login_response.json()
    token = data["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    logout_response = await client.post("/auth/logout", headers=headers)
    assert logout_response.status_code == 200
    assert logout_response.json().get("message") == "Logged out"

    me_response = await client.get("/users/me", headers=headers)
    assert me_response.status_code == 401
