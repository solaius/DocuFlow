from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000  # Using the provided port

    # NVIDIA GPU Settings
    CUDA_HOME: str = "/usr/local/cuda"
    CUDA_PATH: str = "/usr/local/cuda/bin:/usr/local/bin:/usr/bin:/bin"
    CUDA_LD_LIBRARY_PATH: str = "/usr/local/cuda/lib64"
    
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()