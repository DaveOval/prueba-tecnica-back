from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user, auth, images
from app.db.init_db import init_db
from app.utils.logger import app_logger
from app.config import ALLOWED_ORIGINS

app = FastAPI(
    title="API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins= ALLOWED_ORIGINS,  
    allow_credentials=True,  
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    app_logger.info("Starting the app...")
    init_db()
    app_logger.info("Database initialized")

@app.get("/")
async def root():
    app_logger.info("Root endpoint accessed")
    return {"message": "Hello world"}

@app.get("/health")
async def health():
    app_logger.info("Health check endpoint accessed")
    return {"status": "ok"}

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(images.router, prefix="/images", tags=["images"])

app_logger.info("APP STARTED, LET'S GO!!!!! 🚀")