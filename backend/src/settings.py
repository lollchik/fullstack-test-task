from pathlib import Path

from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(BASE_DIR).resolve().parent / ".env.dev")

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    PGPORT: int
    RQ_BROKER_URL: str

    @computed_field
    @property
    def STORAGE_DIR(self) -> Path:
        path = BASE_DIR / "storage" / "files"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @computed_field
    @property
    def DB_URL(self) -> str:
        dsn = PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.PGPORT,
            path=self.POSTGRES_DB,
        )
        return str(dsn)


settings = Settings()
