# config.py — all config from the environment. Nothing hard-coded; nothing local.
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    database_url: str
    service_name: str

def load_settings() -> Settings:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is required")
    return Settings(database_url=url, service_name=os.environ.get("SERVICE_NAME", "service"))
