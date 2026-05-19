# Wallet API

Асинхронное REST API для управления кошельками.  
FastAPI + PostgreSQL + Docker + тесты.

## Функциональность

- GET `/api/v1/wallets/{wallet_uuid}` — получить баланс
- POST `/api/v1/wallets/{wallet_uuid}/operation` — пополнение (DEPOSIT) или снятие (WITHDRAW)

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
- `main` — стабильная версия (работает, Docker собирается)
- `alembic` — текущая разработка (может быть нестабильной)
