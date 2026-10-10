from fastapi import Depends, HTTPException, APIRouter
from app.models.schemas import UserCreate, UserResponse
from app.db.database import get_db_connection
from app.db.database import create_user_in_db
from app.core.security import get_current_user
from app.core.security import hash_password
import sqlite3
import asyncio

router = APIRouter()

@router.post("/users/")
async def create_user(user: UserCreate):
    try:
        res_user = await create_user_in_db(user.name, user.email, hash_password(user.password))
        return {"id": res_user[0], "name": res_user[1], "email": res_user[2]}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="User with that email already exist")

@router.get("/users/")
async def get_all_users():
    await asyncio.sleep(3)
    async with get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute('''SELECT * FROM users''')
        users = await cursor.fetchall()
        return [
            {"id": user[0], "name": user[1], "email": user[2]}
            for user in users
        ]

@router.get("/users/top")
async def get_top_users():
    async with  get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute(
            '''SELECT u.id, u.name, SUM(o.amount) AS amount
            FROM users u 
            INNER JOIN orders o ON u.id = o.user_id
            GROUP BY u.id
            ORDER BY amount DESC
            LIMIT 3;
            ''')
        users = await cursor.fetchall()
        return [
            {
                "id": user[0],
                "name": user[1],
                "amount": user[2]
            }
            for user in users
        ]

@router.get("/users/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.get("/users/{user_id}")
async def get_user(user_id: int):
    async with  get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute('''SELECT * FROM users WHERE id = ?''', [user_id])
        user = await cursor.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            return {"id": user[0], "name": user[1], "email": user[2]}


@router.get("/users/{user_id}/orders")
async def get_user_orders(user_id: int):
    async with  get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute('''SELECT * FROM orders WHERE user_id=?''', [user_id])
        orders = await cursor.fetchall()
        return [
            {
                "id": order[0],
                "user_id": order[1],
                "amount": order[2],
                "created_at": order[3]
            }
            for order in orders
        ]

