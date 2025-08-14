import os
from pydantic import BaseModel
from typing import List

def _split_csv(v: str | None) -> list[str]:
    if not v:
        return []
    return [s.strip() for s in v.split(',') if s.strip()]

class Settings(BaseModel):
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./local.db')
    CORS_ORIGINS: List[str] = _split_csv(os.getenv('CORS_ORIGINS'))
    RUN_MIGRATIONS: bool = os.getenv('RUN_MIGRATIONS', '1') == '1'
    APP_BASE_URL: str | None = os.getenv('APP_BASE_URL')

settings = Settings()
