from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    TESTING: bool = False
    
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    SECRET_KEY: str = Field(..., min_length=32, env="SECRET_KEY")
    ALGORITHM: str = Field(..., env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    FIRST_SUPERUSER_USERNAME: str = Field(..., env="FIRST_SUPERUSER_USERNAME")
    FIRST_SUPERUSER_EMAIL: str = Field(..., env="FIRST_SUPERUSER_EMAIL")
    FIRST_SUPERUSER_PASSWORD: str = Field(..., env="FIRST_SUPERUSER_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=".env.test" if os.getenv("TESTING") == "1" else ".env",
    )


settings = Settings()
