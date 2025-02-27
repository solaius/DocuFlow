from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import documents

app = FastAPI(
    title="DocuFlow API",
    description="A scalable document ingestion pipeline API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/documents", tags=["documents"])

@app.get("/")
async def root():
    return {"message": "Welcome to DocuFlow API"}