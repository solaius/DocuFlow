import uvicorn
from config.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "docuflow.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )