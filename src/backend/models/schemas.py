# src/backend/models/schemas.py
from pydantic import BaseModel
from typing import Literal, Optional, List


class ChatMessage(BaseModel):
    content: str
    agent_type: Literal["react", "reflection", "plan"]


class WSMessage(BaseModel):
    type: Literal["message", "interrupt"]
    data: Optional[ChatMessage] = None


class AgentInfo(BaseModel):
    id: str
    name: str
    description: str


class ToolInfo(BaseModel):
    name: str
    description: str
    available: bool


class TokenData(BaseModel):
    content: str


class WSSResponse(BaseModel):
    type: Literal["token", "thinking", "done", "error"]
    data: dict