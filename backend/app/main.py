from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import os

from .db.session import engine, Base
from .api import auth, ingest, alerts, stats, model

# Create database tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=os.getenv("APP_NAME", "AI Cyber Threat Detection Framework"),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS middleware for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development. Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(model.router, prefix="/api")

@app.get("/health", tags=["health"])
def health_check():
    return {
        "status": "healthy",
        "app": "AI Cyber Threat Detection API",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=os.getenv("HOST", "0.0.0.0"), 
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
