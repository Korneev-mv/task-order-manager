import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import create_tables, config, get_db_connection

pytestmark = pytest.mark.asyncio

client = TestClient(app)


@pytest_asyncio.fixture
async def db_connection():

    old_path = config.path
    config.path = "tests/test.db"

    await create_tables()

    async with get_db_connection() as conn:
        await conn.execute("DELETE FROM orders")
        await conn.execute("DELETE FROM users")
        await conn.commit()

    yield

    async with get_db_connection() as conn:
        await conn.execute("DELETE FROM orders")
        await conn.execute("DELETE FROM users")
        await conn.execute("DELETE FROM tasks")
        await conn.commit()

    config.path = old_path


@pytest_asyncio.fixture
async def auth_token(db_connection):
    # Регистрируем пользователя
    client.post("/auth/register", json={
        "name": "OrderUser",
        "email": "orderuser@mail.ru",
        "password": "12345678"
    })
    # Логинимся
    response = client.post("/auth/login", json={
        "email": "orderuser@mail.ru",
        "password": "12345678"
    })
    return response.json()["access_token"]

async def test_create_user(db_connection):
    response = client.post("/users/", json={"name": "Test", "email": "test12@mail.ru", "password": "12312312"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test"
    assert data["email"] == "test12@mail.ru"


async def test_create_same_user(db_connection):
    client.post("/users/", json={"name": "Test", "email": "test12@mail.ru", "password": "12312312"})

    response = client.post("/users/", json={"name": "Test", "email": "test12@mail.ru", "password": "12312312"})
    assert response.status_code == 400
    assert "already exist" in response.text


async def test_get_users(db_connection):
    client.post("/users/", json={"name": "Test1", "email": "test9@mail.ru", "password": "12312312"})
    client.post("/users/", json={"name": "Test2", "email": "test10@mail.ru", "password": "12312312"})

    request = client.get("/users/")
    assert request.status_code == 200
    data = request.json()

    emails = [user["email"] for user in data]
    assert "test9@mail.ru" in emails
    assert "test10@mail.ru" in emails


async def test_get_user_by_id(db_connection):
    create_response = client.post("/users/", json={"name": "Test", "email": "test99@mail.ru", "password": "12312312"})
    assert create_response.status_code == 200
    created_user = create_response.json()

    user_id = created_user["id"]
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["name"] == "Test"
    assert data["email"] == "test99@mail.ru"


async def test_get_user_not_found(db_connection):
    response = client.get("/users/999")
    assert response.status_code == 404
    assert "not found" in response.text


async def test_create_order(db_connection, auth_token):
    # Создаём заказ с токеном
    response = client.post(
        "/orders/",
        json={"amount": 100.5},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100.5
    # Проверяем, что user_id подставился из токена
    assert data["user_id"] is not None


async def test_get_user_orders(db_connection, auth_token):
    # Создаём заказ
    client.post(
        "/orders/",
        json={"amount": 100.5},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    # Получаем заказы текущего пользователя
    response = client.get(
        "/orders/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["amount"] == 100.5


async def test_get_top_users(db_connection, auth_token):
    # Создаём второго пользователя
    client.post("/auth/register", json={
        "name": "Bob",
        "email": "bob@mail.ru",
        "password": "12345678"
    })
    token2 = client.post("/auth/login", json={
        "email": "bob@mail.ru",
        "password": "12345678"
    }).json()["access_token"]

    # Создаём заказы
    client.post(
        "/orders/",
        json={"amount": 1000},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    client.post(
        "/orders/",
        json={"amount": 500},
        headers={"Authorization": f"Bearer {token2}"}
    )

    response = client.get("/users/top")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["amount"] == 1000
    assert data[1]["amount"] == 500

@pytest_asyncio.fixture
async def auth_token(db_connection):
    # Регистрируем пользователя
    client.post("/auth/register", json={
        "name": "TaskUser",
        "email": "taskuser@mail.ru",
        "password": "12345678"
    })
    # Логинимся
    response = client.post("/auth/login", json={
        "email": "taskuser@mail.ru",
        "password": "12345678"
    })

    return response.json()["access_token"]

async def test_create_task(db_connection, auth_token):
    response = client.post(
        "/tasks/",
        json={
            "title": "Купить продукты",
            "description": "Молоко, хлеб, яйца",
            "status": "todo"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Купить продукты"
    assert data["description"] == "Молоко, хлеб, яйца"
    assert data["status"] == "todo"
    assert data["user_id"] is not None


async def test_get_tasks(db_connection, auth_token):
    client.post(
        "/tasks/",
        json={"title": "Задача 1", "description": "Описание 1"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    client.post(
        "/tasks/",
        json={"title": "Задача 2", "description": "Описание 2"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    response = client.get(
        "/tasks/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    titles = [task["title"] for task in data]
    assert "Задача 1" in titles
    assert "Задача 2" in titles


async def test_get_task_by_id(db_connection, auth_token):
    create_response = client.post(
        "/tasks/",
        json={"title": "Тестовая задача", "description": "Описание"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    task_id = create_response.json()["id"]

    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Тестовая задача"
    assert data["description"] == "Описание"


async def test_update_task(db_connection, auth_token):
    create_response = client.post(
        "/tasks/",
        json={"title": "Старый заголовок", "description": "Старое описание"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    task_id = create_response.json()["id"]

    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Новый заголовок", "status": "done"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Новый заголовок"
    assert data["status"] == "done"
    assert data["description"] == "Старое описание"


async def test_delete_task(db_connection, auth_token):
    create_response = client.post(
        "/tasks/",
        json={"title": "Задача для удаления"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    task_id = create_response.json()["id"]

    response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204

    get_response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_response.status_code == 404


async def test_get_top_tasks(db_connection, auth_token):
    # Создаём двух пользователей
    user1 = client.post("/auth/register", json={
        "name": "User1", "email": "user1@mail.ru", "password": "12345678"
    }).json()
    token1 = client.post("/auth/login", json={
        "email": "user1@mail.ru", "password": "12345678"
    }).json()["access_token"]

    user2 = client.post("/auth/register", json={
        "name": "User2", "email": "user2@mail.ru", "password": "12345678"
    }).json()
    token2 = client.post("/auth/login", json={
        "email": "user2@mail.ru", "password": "12345678"
    }).json()["access_token"]

    # Создаём задачи (user1 — 2 выполненные, user2 — 1 выполненную)
    client.post("/tasks/", json={"title": "Task1", "status": "done"}, headers={"Authorization": f"Bearer {token1}"})
    client.post("/tasks/", json={"title": "Task2", "status": "done"}, headers={"Authorization": f"Bearer {token1}"})
    client.post("/tasks/", json={"title": "Task3", "status": "done"}, headers={"Authorization": f"Bearer {token2}"})
    client.post("/tasks/", json={"title": "Task4", "status": "todo"}, headers={"Authorization": f"Bearer {token2}"})

    # Получаем топ
    response = client.get("/tasks/top")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["tasks_done"] == 2
    assert data[0]["user_id"] == user1["id"]
    assert data[1]["tasks_done"] == 1