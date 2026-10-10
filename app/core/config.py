import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret-key-for-dev")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "app.db")

settings = Settings()