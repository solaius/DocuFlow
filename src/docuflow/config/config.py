from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra='ignore'  # Allow extra fields in environment
    )

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000  # Using the provided port

    # NVIDIA GPU Settings
    CUDA_HOME: Optional[str] = None
    CUDA_PATH: Optional[str] = None
    CUDA_LD_LIBRARY_PATH: Optional[str] = None
    PATH: Optional[str] = None
    LD_LIBRARY_PATH: Optional[str] = None
    
    # Elasticsearch Settings
    ES_HOST: str = "192.168.1.17"
    ES_PORT: int = 9200
    
    # Neo4j Settings
    NEO4J_URI: str = "bolt://192.168.1.17:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "Solius22"
    
    # Document Processing Settings
    UPLOAD_DIR: str = "/tmp/docuflow/uploads"
    PROCESSED_DIR: str = "/tmp/docuflow/processed"

    def get_cuda_settings(self) -> dict:
        """Get CUDA-related settings with platform-specific defaults."""
        import platform
        import os
        
        is_windows = platform.system() == "Windows"
        
        # Get CUDA home
        cuda_home = self.CUDA_HOME
        if not cuda_home:
            if is_windows:
                # Check common Windows CUDA locations
                for version in range(12, 8, -1):  # Try CUDA 12.x down to 9.x
                    path = f"C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v{version}.{version}"
                    if os.path.exists(path):
                        cuda_home = path
                        break
            else:
                # Default Linux location
                cuda_home = "/usr/local/cuda"
        
        # Set paths based on CUDA home
        if cuda_home:
            if is_windows:
                cuda_path = f"{cuda_home}\\bin"
                cuda_lib = f"{cuda_home}\\lib64"
            else:
                cuda_path = f"{cuda_home}/bin"
                cuda_lib = f"{cuda_home}/lib64"
        else:
            cuda_path = ""
            cuda_lib = ""
        
        return {
            "CUDA_HOME": cuda_home,
            "PATH": self.PATH or cuda_path,
            "LD_LIBRARY_PATH": self.LD_LIBRARY_PATH or cuda_lib
        }

settings = Settings()