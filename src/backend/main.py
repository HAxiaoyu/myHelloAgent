# src/backend/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import chat, conversations


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    await init_db()
    yield
    # Shutdown: cleanup if needed


app = FastAPI(
    title="myHelloAgent API",
    description="LLM Agent Web Chat API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(conversations.router)


@app.get("/")
async def root():
    return {"message": "myHelloAgent API", "docs": "/docs"}