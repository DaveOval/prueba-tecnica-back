from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user, auth, images
from app.db.init_db import init_db

app = FastAPI(
    title="API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,  
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    init_db()

@app.get("/")
async def root():
    return {"message": "Hola mundo"}

@app.get("/health")
async def health():
    return {"status": "ok"}

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(images.router, prefix="/images", tags=["images"])