from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from dotenv import load_dotenv, dotenv_values
import os

# ✅ Ensure env vars are loaded early
load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL:str = Field(...)
    SYNC_DATABASE_URL:str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    REDIS_HOST: str = 'localhost'
    REDIS_PORT:int =6379
    REDIS_URL:str ="redis://localhost:6379/0"
    MAIL_USERNAME: str
    MAIL_PASSWORD:str
    MAIL_FROM:str
    MAIL_PORT:int
    MAIL_SERVER:str
    MAIL_FROM_NAME:str
    MAIL_STARTTLS:bool=True
    MAIL_SSL_TLS:bool=False
    USE_CREDENTIALS:bool=True
    VALIDATE_CERTS:bool=True
    DOMAIN:str
    GROQ_API_KEY:str
    OPENAI_API_KEY:str


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

Config = Settings()

#"redis://localhost:6379/0"