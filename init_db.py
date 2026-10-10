from app.db.database import create_tables
import asyncio

if __name__ == "__main__":
    asyncio.run(create_tables())
