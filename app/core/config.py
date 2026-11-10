from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Settings
    api_title: str = "AdBoard API"
    api_description: str = "API description"
    api_version: str = "1.0.0"
    api_host: str = "0.0.0.0"
    api_port: int = 8880
    debug: bool = True

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    task_max_retries: int = 5
    task_retry_delay: float = 10
    task_max_retry_delay: float = 300

    # dev / prod / pytest
    environment: str = "dev"

    # logger
    LOG_LEVEL: str = "INFO"

    # Jwt
    secret_key: str
    algorithm: str = "HS256"
    access_token_expires_minutes: int = 15
    refresh_token_expire_days: int = 7

    # Email
    email_server: str
    email_port: int
    email_user: str
    email_password: str
    email_from: EmailStr
    email_from_name: str

    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8', 
        extra='ignore'
    )

    def get_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def get_test_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/adboard_test"

    def get_db_url_for_alembic(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

settings = Settings()
