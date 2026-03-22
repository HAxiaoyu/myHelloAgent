# src/backend/models/schemas.py
from datetime import datetime
from typing import Literal, Optional, List

from pydantic import BaseModel


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


class MessageResponse(BaseModel):
    """Schema for message in conversation response."""
    id: int
    role: str
    content: str
    thinking: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""
    title: Optional[str] = "New Conversation"
    agent_type: str = "react"


class ConversationUpdate(BaseModel):
    """Schema for updating conversation metadata."""
    title: Optional[str] = None
    agent_type: Optional[str] = None


class ConversationResponse(BaseModel):
    """Schema for conversation list item."""
    id: int
    title: str
    agent_type: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    class Config:
        from_attributes = True


class ConversationDetail(BaseModel):
    """Schema for full conversation with messages."""
    id: int
    title: str
    agent_type: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Schema for creating a message."""
    role: str
    content: str
    thinking: Optional[str] = None