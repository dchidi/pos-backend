from typing import List, Optional
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    APP_NAME: str = "ScanPay"
    PROJECT_NAME: str = "ScanPay API"
    APP_BASE_URL: str = "http://127.0.0.1:8000/api/v1" # Update this on .env file to point to the server

    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "scanpay_db"
    # MONGO_DB_NAME: str = "scanpay_db_dev"
    # MONGO_DB_NAME: str = "scanpay_db_prod"    
    # MONGO_DB_NAME: str = "scanpay_db_uat"

    SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30    
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "youremail@gmail.com"
    SMTP_PASSWORD: str = "yourapppassword"
    FROM_EMAIL: str = "youremail@gmail.com"

    PROJECT_VERSION: str = 'v1.0.0'

    OTP_EXPIRY_TIME_MINUTES: int = 30
    ACCOUNT_VERIFICATION_EXPIRY_TIME_HOURS: int = 24

    REDIRECT_TO_UPDATE_PASSWORD: str = "http://localhost:5173/update_password"

    CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]  # or ["*"] for all
    ACTIVATION_LINK: str = "http://127.0.0.1:8000/api/v1/auth/verify_account?verification_token="

    

    # Paystack
    PAYSTACK_SECRET_KEY: str
    PAYSTACK_PUBLIC_KEY: Optional[str] = None
    PAYSTACK_BASE_URL: AnyHttpUrl = "https://api.paystack.co" # type: ignore


    # Webhook
    WEBHOOK_SECRET_SAME_AS_PAYSTACK_SECRET: bool = True
    WEBHOOK_SECRET: Optional[str] = None


    # HTTP
    HTTP_TIMEOUT_SECONDS: float = 15.0

    class Config:
        env_file = ".env"

settings = Settings()
