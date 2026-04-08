import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "aesir-dev-key")
    TEMPLATES_AUTO_RELOAD = True
