"""
Core Configuration Settings
Professional Mewayz Platform
"""
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    # Database
    MONGO_URL: str = os.getenv("MONGODB_URL", os.getenv("DATABASE_URL", "mongodb://localhost:27017/mewayz"))
    DATABASE_NAME: str = "mewayz"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "mewayz-professional-secret-key-2025-ultra-secure")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "super-secret-session-key")
    
    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    
    # Payment
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = os.getenv("STRIPE_PUBLISHABLE_KEY")
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Application
    APP_NAME: str = "Mewayz Professional Platform"
    VERSION: str = "3.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS Settings
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://mewayz.com",
        "https://*.mewayz.com"
    ]

settings = Settings()