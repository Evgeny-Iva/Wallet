# Wallet API

Асинхронное REST API для управления кошельками.  
FastAPI + PostgreSQL + Docker + тесты.

## Функциональность

### Кошельки
- POST `/wallets/` - создание кошелька
- GET `/wallets/{wallet_uuid}` - получить баланс
- POST `/wallets/{wallet_uuid}/operation` - пополнение (DEPOSIT) или снятие (WITHDRAW)
- POST `/{wallet_id}/transfer` - Выполняет операцию перевода между кошельками

### Пользователи
- POST `/auth/register` - регистрация пользователя
- POST `/auth/login` - авторизация пользователя
- POST `/auth/logout` - сброс сессии
- GET `/users/me` - получение данных о пользователе

## Запуск

## Миграции

Миграции управляются через **Alembic**.

### Применить миграции

```bash
  alembic upgrade head
```

### Локально

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
2. Создайте файл .env с переменной DATABASE_URL (пример в .env.example)
3. Примените миграции:
    ```bash
    python migrate.py
4. Запуск сервера:
    ```bash
    uvicorn api.main:app --reload

### Через докер
```bash
  docker-compose up --build
```

После запуска документация доступна по адресу:
http://localhost:8000/docs

## Тесты
```bash
  pytest -v
```

### Стеки
- Python 3.13
- FastAPI
- PostgreSQL (asyncpg)
- SQLAlchemy 2.0
- Alembic (миграции)
- Docker / docker-compose
- pytest / httpx

## Ветки проекта
- `master` — стабильная версия (работает, Docker собирается)
- `development` — текущая разработка (может быть нестабильной)
