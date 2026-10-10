import aiosqlite
from app.core.config import settings

class DatabaseConfig:
    def __init__(self):
        self.path = settings.DATABASE_URL
        self._connection = None

config = DatabaseConfig()

def get_db_connection():
    return aiosqlite.connect(config.path)

async def create_tables(conn=None):
    if conn is None:
        conn = get_db_connection()
    async with conn:
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        await conn.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'todo',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')

async def get_user_by_id(user_id: int) -> tuple | None:
    async with get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute('''SELECT * FROM users WHERE id = ?''', [user_id])
        return await cursor.fetchone()

async def create_user_in_db(name: str, email: str, hashed_password: str) -> tuple:
    async with  get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute('''INSERT INTO users (name, email, password) VALUES (?, ?, ?);''', [name, email, hashed_password])
        last_id = cursor.lastrowid
        await connection.commit()
        await cursor.execute('''SELECT * FROM users WHERE id = ?''', [last_id])
        return await cursor.fetchone()