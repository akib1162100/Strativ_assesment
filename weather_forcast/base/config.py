import os
from load_dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("Weather_DB_USER", "postgres")
DB_PASSWORD = os.getenv("Weather_DB_PASSWORD", "mis123")
DB_HOST = os.getenv("Weather_HOST", "localhost")
DB_PORT = os.getenv("Weather_PORT", "5432")
DB_NAME = os.getenv("Weather_DB_NAME", "weather_db")

SECRET = os.getenv(
    "Weather_SECRET",
    "a92d1aa5f67ce24713cf638550f5daa84ef5ea3466ae29af8b1ad16fbe6c5fbb",
)

DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


class Config:
    DB_USER = os.getenv("Weather_DB_USER", "postgres")
    DB_PASSWORD = os.getenv("Weather_DB_PASSWORD", "mis123")
    DB_NAME = os.getenv("Weather_DB_NAME", "weather_db")
    DB_HOST = os.getenv("Weather_HOST", "localhost")
    DB_CONFIG = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
