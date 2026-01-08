from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.routes import items, external_api
import uvicorn
import os

# Import models
from app.models import item_model

# Create tables function (will be called on startup)
async def create_tables():
    from app.database import engine
    item_model.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(
    title="Python Backend Engineer Take Home Assessment API",
    description="A robust REST API service using FastAPI and PostgreSQL that acts as a bridge between a local database and an external API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(items.router, prefix="/api/v1", tags=["items"])
app.include_router(external_api.router, prefix="/api/v1", tags=["external"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Python Backend Engineer Take Home Assessment API"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)