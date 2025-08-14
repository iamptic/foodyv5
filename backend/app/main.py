from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .settings import settings
from .db import create_all
from . import schemas
from .api import router as api_router

app = FastAPI(title="Foody Backend", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS or ["*"],  # Canvas stage: permissive if not set
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=schemas.HealthOut)
def health():
    return {"status": "ok"}

@app.get("/ready", response_model=schemas.HealthOut)
def ready():
    return {"status": "ok"}

app.include_router(api_router)

# DB bootstrap (create tables)
if settings.RUN_MIGRATIONS:
    create_all()
