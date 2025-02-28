import os
from typing import ClassVar

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application Settings
    APP_NAME: str = "DocuFlow"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # File Storage Settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {"pdf", "png", "jpg", "jpeg", "tiff", "docx", "html"}
    
    # Processing Settings
    MAX_PAGES: int = 100
    PROCESSING_TIMEOUT: int = 300  # 5 minutes
    
    # NVIDIA GPU Settings
    CUDA_HOME: ClassVar[str] = '/usr/local/cuda'
    PATH: str = os.getenv('PATH', '')
    LD_LIBRARY_PATH: str = os.getenv('LD_LIBRARY_PATH', '')
    TORCH_CUDA_ARCH_LIST: str = os.getenv('TORCH_CUDA_ARCH_LIST', '8.9+PTX')
    
    # Model Settings
    USE_GPU: bool = True
    BATCH_SIZE: int = 4
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()