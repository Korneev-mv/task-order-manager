from app.models.schemas import OrderResponse, OrderCreate
from app.db.database import get_db_connection
from fastapi import HTTPException, APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.post("/orders/", response_model=OrderResponse)
async def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    async with get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute('''SELECT id FROM users WHERE id = ?''', [user_id])
        user = await cursor.fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        await cursor.execute('''INSERT INTO orders (user_id, amount) VALUES (?,?)''', [user_id, order.amount])
        await connection.commit()
        last_id = cursor.lastrowid
        await cursor.execute('''SELECT * FROM orders WHERE id = ?''', [last_id])
        new_order = await cursor.fetchone()
        return {
            "id": new_order[0],
            "user_id": new_order[1],
            "amount": new_order[2],
            "created_at": new_order[3]
        }

@router.get("/orders/me")
async def get_all_orders(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
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
