from conftest import client
import pytest_asyncio


async def register_test_user(client):
    """Создаем пользователя для использования в тестах"""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "secret123"
    }
    response = await client.post("/auth/register", json=user_data)
    return response, user_data



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


async def test_register_duplicate_email(client):
    """Проверяет повторное создания пользователя по одному email"""
    response_first, user_data = await register_test_user(client)

    assert response_first.status_code == 200

    response_second = await client.post("/auth/register", json=user_data)
    assert response_second.status_code == 400
    assert response_second.json()["detail"] == "Email already register"


async def test_login_success(client):
    """Логин с верным паролем"""
    response, user_data = await register_test_user(client)

    assert response.status_code == 200

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    login_response = await client.posta("/auth/login", json=login_data)
    assert login_response.status_code == 200

    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"] != ""
