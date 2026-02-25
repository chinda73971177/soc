from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://socuser:socpassword@localhost:5432/socdb"
    redis_url: str = "redis://:redispassword@localhost:6379/0"
    elasticsearch_url: str = "http://localhost:9200"
    kafka_bootstrap_servers: str = "localhost:9092"
    secret_key: str = "supersecretkey-change-in-production-minimum-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token: Optional[str] = None
    twilio_whatsapp_from: Optional[str] = None
    whatsapp_to: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
