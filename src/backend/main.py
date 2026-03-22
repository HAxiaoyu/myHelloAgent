# src/backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import chat

app = FastAPI(
    title="myHelloAgent API",
    description="LLM Agent Web Chat API",
    version="1.0.0",
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


@app.get("/")
async def root():
    return {"message": "myHelloAgent API", "docs": "/docs"}