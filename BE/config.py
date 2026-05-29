import os


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


DB_HOST = _env("DB_HOST", "db")
DB_PORT = _env("DB_PORT", "3306")
DB_USER = _env("DB_USER", "root")
DB_PASSWORD = _env("DB_PASSWORD", "password")
DB_NAME = _env("DB_NAME", "servisracunara")

DATABASE_URL = _env(
    "DATABASE_URL",
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)
