from typing import List
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    APP_NAME: str = "ScanPay"
    PROJECT_NAME: str = "ScanPay API"
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "scanpay_db"
    SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "youremail@gmail.com"
    SMTP_PASSWORD: str = "yourapppassword"
    FROM_EMAIL: str = "youremail@gmail.com"

    PROJECT_VERSION: str = 'v1.0.0'

    OTP_EXPIRY_TIME_MINUTES: int = 30

    CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]  # or ["*"] for all

    class Config:
        env_file = ".env"

settings = Settings()
