# src/backend/routers/conversations.py
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models.db_models import Conversation, Message
from ..models.schemas import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationDetail,
    MessageCreate,
    MessageResponse,
)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])

@router.get("", response_model=List[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_session)
):
    """List all conversations with message count."""
    result = await session.execute(
        select(
            Conversation,
            func.count(Message.id).label("message_count")
        )
        .outerjoin(Message)
        .group_by(Conversation.id)
        .order_by(Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )

    conversations = []
    for row in result:
        conv = row.Conversation
        conversations.append(ConversationResponse(
            id=conv.id,
            title=conv.title,
            agent_type=conv.agent_type,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            message_count=row.message_count
        ))
    return conversations

@router.post("", response_model=ConversationResponse)
async def create_conversation(
    data: ConversationCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new conversation."""
    conv = Conversation(
        title=data.title,
        agent_type=data.agent_type
    )
    session.add(conv)
    await session.commit()
    await session.refresh(conv)
    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        agent_type=conv.agent_type,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0
    )

@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get a conversation with all messages."""
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    msg_result = await session.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = msg_result.scalars().all()

    return ConversationDetail(
        id=conv.id,
        title=conv.title,
        agent_type=conv.agent_type,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        messages=[
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                thinking=m.thinking,
                created_at=m.created_at
            ) for m in messages
        ]
    )

@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    data: ConversationUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update conversation title or agent type."""
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    if data.title is not None:
        conv.title = data.title
    if data.agent_type is not None:
        conv.agent_type = data.agent_type

    await session.commit()
    await session.refresh(conv)

    count_result = await session.execute(
        select(func.count(Message.id)).where(Message.conversation_id == conversation_id)
    )
    message_count = count_result.scalar()

    return ConversationResponse(
        id=conv.id,
        title=conv.title,
        agent_type=conv.agent_type,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=message_count
    )

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete a conversation and all its messages."""
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    await session.delete(conv)
    await session.commit()
    return {"message": "Conversation deleted"}

@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def add_message(
    conversation_id: int,
    data: MessageCreate,
    session: AsyncSession = Depends(get_session)
):
    """Add a message to a conversation."""
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    msg = Message(
        conversation_id=conversation_id,
        role=data.role,
        content=data.content,
        thinking=data.thinking
    )
    session.add(msg)

    conv.updated_at = datetime.now(timezone.utc)

    await session.commit()
    await session.refresh(msg)

    return MessageResponse(
        id=msg.id,
        role=msg.role,
        content=msg.content,
        thinking=msg.thinking,
        created_at=msg.created_at
    )