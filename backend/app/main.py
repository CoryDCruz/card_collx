from contextlib import asynccontextmanager
import hashlib
import logging
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api import routes
from app.core.config import settings
from app.db.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    init_db()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="Card Collection Tracker API",
    description="API for tracking sports card collections",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Only mount local static files when using local storage
if settings.STORAGE_TYPE == "local":
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

# Include API routes
app.include_router(routes.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Card Collection Tracker API", "version": "0.1.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# eBay Marketplace Account Deletion webhook
@app.get("/ebay/account-deletion")
async def ebay_deletion_challenge(challenge_code: str = Query(...)):
    """Respond to eBay's endpoint verification challenge."""
    token = settings.EBAY_VERIFICATION_TOKEN
    endpoint = settings.EBAY_DELETION_ENDPOINT
    hash_input = challenge_code + token + endpoint
    challenge_response = hashlib.sha256(hash_input.encode()).hexdigest()
    return {"challengeResponse": challenge_response}


@app.post("/ebay/account-deletion")
async def ebay_deletion_notification():
    """Acknowledge eBay account deletion notifications. We don't store eBay user data."""
    return {"status": "ok"}
