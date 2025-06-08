from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Servicio de Usuarios"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Supabase configuration
    SUPABASE_URL: str = ''
    SUPABASE_PASSWORD: str 
    SUPABASE_DB_URL: Optional[str] = None
    
    # Security configuration
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 