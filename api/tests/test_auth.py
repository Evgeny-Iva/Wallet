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
    login_response = await client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"] != ""


async def test_login_wrong_password(client):
    """Тест авторизации с не правильным паролем"""
    response, user_data = await register_test_user(client)
    assert response.status_code == 200

    login_data = {"email": user_data["email"], "password": "password"}
    login_response = await client.post("/auth/login", json=login_data)
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Unauthorized"


async def test_login_user_not_found(client):
    """Тест на не существующего пользователя"""
    login_data = {"email": "test@example.com", "password": "secret123"}
    login_response = await client.post("/auth/login", json=login_data)
    assert login_response.status_code == 404
    assert login_response.json()["detail"] == "Not Found"


async def test_me_unauthorized(client):
    """Тест на проверку получения данных будучи не авторизованным"""
    login_response = await client.post("/users/me")
    assert login_response.status_code == 401
    assert login_response.json()["detail"] == "Not authenticated"


async def test_me_success(client):
    """Тест на получение данных авторизованным пользователем"""
    response, user_data = await register_test_user(client)
    assert response.status_code == 200

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    login_response = await client.post("/users/me", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_response = await client.get("/users/me", headers=headers)
    assert me_response.status_code == 200

    me_data = me_response.json()
    assert me_data["email"] == user_data["email"]
    assert me_data["first_name"] == user_data["first_name"]
    assert me_data["last_name"] == user_data["last_name"]
    assert "id" in me_data
    assert "created_at" in me_data


async def test_logout_success(client):
    """Тест на выход из профиля"""
    response, user_data = await register_test_user(client)
    assert response.status_code == 200

    login_data = {"email": user_data["email"], "password": user_data["password"]}
    login_response = await client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200

    data = login_response.json()
    token = data["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    logout_response = await client.post("/auth/logout", headers=headers)
    me_response = await client.get("/users/me", headers=headers)
    assert me_response.status_code == 401
