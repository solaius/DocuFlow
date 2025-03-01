from docuflow.config.config import settings

def main():
    print("Current Settings:")
    print("-" * 40)
    
    # Show API settings
    print("\nAPI Settings:")
    print(f"Host: {settings.API_HOST}")
    print(f"Port: {settings.API_PORT}")
    
    # Show CUDA settings
    print("\nCUDA Settings:")
    cuda_settings = settings.get_cuda_settings()
    for key, value in cuda_settings.items():
        print(f"{key}: {value}")
    
    # Show storage settings
    print("\nStorage Settings:")
    print(f"Upload Dir: {settings.UPLOAD_DIR}")
    print(f"Processed Dir: {settings.PROCESSED_DIR}")
    
    # Show database settings
    print("\nDatabase Settings:")
    print(f"Elasticsearch: {settings.ES_HOST}:{settings.ES_PORT}")
    print(f"Neo4j: {settings.NEO4J_URI}")

if __name__ == "__main__":
    main()