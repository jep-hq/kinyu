from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, PostgresDsn, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Kinyu Headless Commerce"
    API_V1_STR: str = "/api/v1"

    # DATABASE
    DATABASE_URL: PostgresDsn = "postgresql+asyncpg://user:password@localhost:5432/kinyu_db"

    # SECURITY
    SECRET_KEY: str = "changethis_secretkey_generated_securely"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # MOLLIE
    MOLLIE_API_KEY: str = ""
    MOLLIE_WEBHOOK_URL: str = "" # Public URL for webhook

    # EMAIL
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "info@kinyu.com"
    EMAILS_FROM_NAME: str = "Kinyu"
    # ZITADEL / IAM
    ZITADEL_ISSUER: str = "http://localhost:8080"
    ZITADEL_PROJECT_ID: str = ""
    ZITADEL_CLIENT_ID: str = "" # Public Client ID for Frontend
    ZITADEL_API_AUDIENCE: str = "" # Audience for API verification
    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")

settings = Settings()
