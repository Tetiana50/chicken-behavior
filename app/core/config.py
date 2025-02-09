from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Video Processing API"
    
    # Development settings
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # Storage paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    STORAGE_DIR: Path = BASE_DIR / "storage"
    VIDEO_DIR: Path = STORAGE_DIR / "videos"
    FRAME_DIR: Path = STORAGE_DIR / "frames"
    
    # Video processing settings
    FRAME_INTERVAL: int = 10  # Extract frame every 10 seconds
    MAX_VIDEO_SIZE_MB: int = 500
    SUPPORTED_VIDEO_FORMATS: set = {".mp4", ".avi", ".mov", ".mkv"}
    
    # OpenAI settings (if needed later)
    OPENAI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create storage directories
def create_directories():
    settings = Settings()
    settings.STORAGE_DIR.mkdir(exist_ok=True)
    settings.VIDEO_DIR.mkdir(exist_ok=True)
    settings.FRAME_DIR.mkdir(exist_ok=True)

# Initialize settings
settings = Settings()
create_directories() 