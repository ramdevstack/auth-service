from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # ----------------------------------------
    # 1. DATABASE
    # ----------------------------------------
    # Falls back to SQLite if DATABASE_URL not set in .env
    database_url: str = "sqlite:///./auth.db"

    # ----------------------------------------
    # 2. JWT SETTINGS
    # ----------------------------------------
    # Secret key — used to sign tokens. Keep this private.
    secret_key: str = "fallback-secret-key"

    # Algorithm used to sign JWT tokens.
    # HS256 (HMAC-SHA256) is the most common — fast and secure.
    algorithm: str = "HS256"

    # How long a token stays valid (in minutes).
    # After this, the user must log in again.
    access_token_expire_minutes: int = 30

    # ----------------------------------------
    # 3. APP SETTINGS
    # ----------------------------------------
    app_name: str = "Auth Service"
    debug: bool = True

    # ----------------------------------------
    # 4. TELL PYDANTIC WHERE TO FIND .env
    # ----------------------------------------
    # This inner class tells Pydantic to automatically
    # read values from the .env file in your project root.
    # env_file=".env" → look for a file called .env
    # case_sensitive=False → SECRET_KEY and secret_key are the same
    class Config:
        env_file = ".env"
        case_sensitive = False

# ----------------------------------------
# 5. SINGLE INSTANCE
# ----------------------------------------
# Create ONE settings object that the whole app imports.
# This is the Singleton pattern — one shared instance everywhere.
# Other files do: from app.core.config import settings
settings = Settings()