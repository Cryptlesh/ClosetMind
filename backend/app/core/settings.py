from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    GEMINI_API_KEY: Optional[str] = None
    WEATHER_API_BASE_URL: str = "https://api.open-meteo.com/v1"
    MCP_TOOLBOX_AlloyDB_POSTGRES_URL: Optional[str] = None
    GOOGLE_CALENDAR_TOKEN: Optional[str] = None
    BASE_URL: str = "http://localhost:8000"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
