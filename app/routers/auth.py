from app.models.schemas import UserLogin, UserRegister, UserResponse, TokenResponse
from app.db.database import get_db_connection
from app.core.security import create_access_token, verify_password, hash_password
from fastapi import HTTPException, APIRouter
from sqlite3 import IntegrityError

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse)
async def register(user: UserRegister):
    try:
        async with get_db_connection() as connection:
            cursor = await connection.cursor()
            await cursor.execute('''INSERT INTO users (name, email, password) VALUES (?,?,?)''', [user.name, user.email, hash_password(user.password)])
            last_id = cursor.lastrowid
            await connection.commit()
            await cursor.execute("SELECT id, name, email FROM users WHERE id = ?", [last_id])
            user = await cursor.fetchone()
            return UserResponse(id=user[0], name=user[1], email=user[2])

    except IntegrityError:
        raise HTTPException(status_code=422, detail="User with that email already exists")

@router.post("/auth/login", response_model=TokenResponse)
async def login(user: UserLogin):
    async with get_db_connection() as connection:
        cursor = await connection.cursor()
        await cursor.execute('''SELECT * FROM users WHERE email = ?''', [user.email])
        usr = await cursor.fetchone()
        if usr is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        hashed_password  = usr[3]
        if not verify_password(user.password, hashed_password ):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token_data = {"sub": str(usr[0])}
        return TokenResponse(access_token=create_access_token(token_data), token_type="bearer")



