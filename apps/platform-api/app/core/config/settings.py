from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Sagesai"
    APP_DESCRIPTION: str = (
        "Enterprise AI Platform for intelligent engineering, "
        "information management, corporate governance, and cybersecurity."
    )
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    API_V1_PREFIX: str = "/api/v1"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

        # Security
    CORS_ORIGINS: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000"
    )
    TRUSTED_HOSTS: str = (
        "localhost,"
        "127.0.0.1,"
        "testserver"
    )
    MAX_REQUEST_SIZE_MB: int = 10
    RATE_LIMIT: str = "100/minute"

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def trusted_hosts_list(self) -> list[str]:
        return [
            host.strip()
            for host in self.TRUSTED_HOSTS.split(",")
            if host.strip()
        ]

    @property
    def MAX_REQUEST_SIZE_BYTES(self) -> int:
        return self.MAX_REQUEST_SIZE_MB * 1024 * 1024

    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "sagesai"
    DATABASE_USER: str = "sagesai"
    DATABASE_PASSWORD: str = "sagesai_dev_password"

    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # AI Gateway
    GEMINI_API_KEY: str = ""
    AI_MODEL: str = "gemini-2.5-flash"
    AI_TEMPERATURE: float = 0.2
    AI_MAX_OUTPUT_TOKENS: int = 2048

    # Internal services
    ANOMALY_SERVICE_URL: str = "http://127.0.0.1:8001"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:"
            f"{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:"
            f"{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
