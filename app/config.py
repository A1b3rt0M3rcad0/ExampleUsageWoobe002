from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    atlas_env: str = "development"
    atlas_host: str = "0.0.0.0"
    atlas_port: int = 8080
    atlas_database_path: str = "./data/atlas.db"
    atlas_storage_path: str = "./data/uploads"
    atlas_max_upload_mb: int = 20

    atlas_woobe_tool_token: str = ""

    woobe_base_url: str = "http://localhost:8000"
    woobe_runtime_key: str = ""
    woobe_timeout_seconds: float = 180.0

    @property
    def database_path(self) -> Path:
        return Path(self.atlas_database_path)

    @property
    def storage_path(self) -> Path:
        return Path(self.atlas_storage_path)


@lru_cache
def get_settings() -> Settings:
    return Settings()
