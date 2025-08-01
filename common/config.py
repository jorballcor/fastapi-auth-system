from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
import os
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    TESTING: bool = False

    DATABASE_URL: str = Field(...)
    TEST_DATABASE_URL: Optional[str] = Field(default=None)

    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = Field(...)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30)

    FIRST_SUPERUSER_USERNAME: str = Field(...)
    FIRST_SUPERUSER_EMAIL: str = Field(...)
    FIRST_SUPERUSER_PASSWORD: str = Field(...)

    model_config = SettingsConfigDict(
        env_file=".env.test" if os.getenv("TESTING") == "1" else ".env",
    )

    @model_validator(mode="before")
    def _assign_db_url(cls, values: dict) -> dict:
        # replicates your v1 root_validator logic
        if values.get("TESTING") and values.get("TEST_DATABASE_URL"):
            values["DATABASE_URL"] = values["TEST_DATABASE_URL"]
        return values

@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")