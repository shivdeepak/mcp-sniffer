import os

from pydantic import BaseModel


class AppConfig(BaseModel):
    LISTEN_HOST: str = os.getenv("LISTEN_HOST", "127.0.0.1")
    LISTEN_PORT: int = int(os.getenv("LISTEN_PORT", "3002"))

    UPSTREAM_HOST: str = os.getenv("UPSTREAM_HOST", "127.0.0.1")
    UPSTREAM_PORT: int = int(os.getenv("UPSTREAM_PORT", "3001"))

    WEB_UI_HOST: str = os.getenv("WEB_UI_HOST", "127.0.0.1")
    WEB_UI_PORT: int = int(os.getenv("WEB_UI_PORT", "8888"))

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


config = AppConfig()
