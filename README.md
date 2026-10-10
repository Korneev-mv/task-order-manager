# Task & Order Manager — REST API на FastAPI

REST API для управления пользователями, заказами и задачами с JWT-авторизацией, асинхронной работой с БД, тестами и Docker.

## Стек

- Python 3.12
- FastAPI
- SQLite + aiosqlite (асинхронная работа с БД)
- SQLAlchemy
- JWT (python-jose) + passlib (pbkdf2_sha256)
- pytest + pytest-asyncio
- Docker + Docker Compose

## Функционал

- Аутентификация: регистрация, логин, JWT-токены
- Пользователи: список, профиль, топ по заказам и задачам
- Заказы: создание, список своих заказов
- Задачи: CRUD (создание, чтение, обновление, удаление), смена статуса
- Калькулятор: арифметические операции с обработкой ошибок
- GitHub API: получение данных пользователя через внешнее API
- Статика: простая HTML/JS-страница для логина и работы с задачами

## Архитектура

app/core/ — config, security (JWT, хеширование)
app/db/ — подключение к БД, создание таблиц
app/models/ — Pydantic-схемы
app/routers/ — эндпоинты
app/services/ — бизнес-логика
app/main.py — точка входа

## Запуск

### Локально

1. Клонировать репозиторий:
```bash
git clone https://github.com/korneev-mv/task-order-manager.git
cd task-order-manager
```
2. Создать виртуальное окружение:
```bash
python -m venv .venv
source .venv/bin/activate  (Linux/macOS)
.venv\Scripts\activate     (Windows)
```
3. Установить зависимости:
```bash
pip install -r requirements.txt
```
4. Создать .env:
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=app.db
```

5. Инициализировать БД:
```bash
python init_db.py
```

6. Запустить:
```bash
uvicorn app.main:app --reload
```
http://localhost:8000/docs — Swagger-документация.

## API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | /auth/register | Регистрация |
| POST | /auth/login | Логин (JWT) |
| GET | /users/me | Профиль текущего пользователя |
| GET | /users/ | Список пользователей |
| GET | /users/top | Топ по сумме заказов |
| POST | /orders/ | Создать заказ |
| GET | /orders/me | Мои заказы |
| POST | /tasks/ | Создать задачу |
| GET | /tasks/ | Мои задачи |
| PUT | /tasks/{id} | Обновить задачу |
| DELETE | /tasks/{id} | Удалить задачу |
| GET | /tasks/top | Топ по выполненным задачам |
| GET | /github/{username} | Данные пользователя GitHub |
| POST | /calculate/ | Калькулятор |
