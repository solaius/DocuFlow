from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 52292  # Using the provided port
    
    # Elasticsearch Settings
    ES_HOST: str = "localhost"
    ES_PORT: int = 9200
    
    # Neo4j Settings
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # Document Processing Settings
    UPLOAD_DIR: str = "/tmp/docuflow/uploads"
    PROCESSED_DIR: str = "/tmp/docuflow/processed"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()