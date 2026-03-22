# Conversation Persistence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add conversation history persistence using SQLite database so users can save, reload, and manage their chat conversations.

**Architecture:** SQLite database with SQLAlchemy ORM for storage, new REST endpoints for conversation CRUD, frontend integration to load/save conversations automatically.

**Tech Stack:** SQLite, SQLAlchemy (async), Pydantic models, FastAPI endpoints, Vue 3 frontend

---

## File Structure

### Backend (New Files)
- `src/backend/database.py` - Database connection and session management
- `src/backend/models/db_models.py` - SQLAlchemy ORM models (Conversation, Message)
- `src/backend/routers/conversations.py` - REST API endpoints for conversation CRUD

### Backend (Modified Files)
- `src/backend/models/schemas.py` - Add Pydantic schemas for API
- `src/backend/main.py` - Register new router, add startup/shutdown events
- `src/backend/routers/chat.py` - Save messages during WebSocket chat
- `src/backend/services/agent_service.py` - Pass conversation_id to save messages
- `pyproject.toml` - Add SQLAlchemy and aiosqlite dependencies

### Frontend (Modified Files)
- `src/frontend/src/api.js` - Add conversation API functions
- `src/frontend/src/App.vue` - Integrate persistence with conversation state

---

## Task 1: Add Database Dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add SQLAlchemy and aiosqlite dependencies**

Add to `pyproject.toml` dependencies:

```toml
dependencies = [
    # ... existing dependencies ...
    "sqlalchemy>=2.0.0",
    "aiosqlite>=0.19.0",
]
```

- [ ] **Step 2: Install dependencies**

Run: `uv sync`
Expected: Dependencies installed successfully

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add SQLAlchemy and aiosqlite for database persistence"
```

---

## Task 2: Create Database Connection Module

**Files:**
- Create: `src/backend/database.py`

- [ ] **Step 1: Create database.py with async engine setup**

```python
# src/backend/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

# Database URL - SQLite file in project root
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./conversations.db")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    """Dependency for getting async session."""
    async with async_session_maker() as session:
        yield session
```

- [ ] **Step 2: Commit**

```bash
git add src/backend/database.py
git commit -m "feat: add async database connection module with SQLite support"
```

---

## Task 3: Create Database Models

**Files:**
- Create: `src/backend/models/db_models.py`

- [ ] **Step 1: Create ORM models for Conversation and Message**

```python
# src/backend/models/db_models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), default="New Conversation")
    agent_type = Column(String(50), default="react")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    thinking = Column(Text, nullable=True)  # Thinking content for assistant messages
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to conversation
    conversation = relationship("Conversation", back_populates="messages")
```

- [ ] **Step 2: Commit**

```bash
git add src/backend/models/db_models.py
git commit -m "feat: add SQLAlchemy ORM models for Conversation and Message"
```

---

## Task 4: Add Pydantic Schemas

**Files:**
- Modify: `src/backend/models/schemas.py`

- [ ] **Step 1: Add conversation-related Pydantic schemas**

Add to existing `schemas.py`:

```python
from datetime import datetime
from typing import List, Optional

# ... existing imports and models ...

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
```

- [ ] **Step 2: Commit**

```bash
git add src/backend/models/schemas.py
git commit -m "feat: add Pydantic schemas for conversation API"
```

---

## Task 5: Create Conversation Router

**Files:**
- Create: `src/backend/routers/conversations.py`

- [ ] **Step 1: Create CRUD endpoints for conversations**

```python
# src/backend/routers/conversations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

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
    # Query conversations with message count
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
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
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
        raise HTTPException(status_code=404, detail="Conversation not found")

    if data.title is not None:
        conv.title = data.title
    if data.agent_type is not None:
        conv.agent_type = data.agent_type

    await session.commit()
    await session.refresh(conv)

    # Get message count
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
        raise HTTPException(status_code=404, detail="Conversation not found")

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
    # Verify conversation exists
    result = await session.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conv = result.scalar_one_or_none()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    msg = Message(
        conversation_id=conversation_id,
        role=data.role,
        content=data.content,
        thinking=data.thinking
    )
    session.add(msg)

    # Update conversation updated_at
    from datetime import datetime
    conv.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(msg)

    return MessageResponse(
        id=msg.id,
        role=msg.role,
        content=msg.content,
        thinking=msg.thinking,
        created_at=msg.created_at
    )
```

- [ ] **Step 2: Commit**

```bash
git add src/backend/routers/conversations.py
git commit -m "feat: add conversation CRUD API endpoints"
```

---

## Task 6: Register Router and Initialize Database

**Files:**
- Modify: `src/backend/main.py`

- [ ] **Step 1: Import and register conversation router with database init**

Read current `main.py` and update:

```python
# src/backend/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import chat, conversations
from .database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    await init_db()
    yield
    # Shutdown: cleanup if needed

app = FastAPI(title="myHelloAgent API", lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(conversations.router)

@app.get("/")
async def root():
    return {"message": "myHelloAgent API is running"}
```

- [ ] **Step 2: Commit**

```bash
git add src/backend/main.py
git commit -m "feat: register conversation router and initialize database on startup"
```

---

## Task 7: Update Frontend API Client

**Files:**
- Modify: `src/frontend/src/api.js`

- [ ] **Step 1: Add conversation API functions**

Add to existing `api.js`:

```javascript
// ... existing code ...

// Conversation API
export async function getConversations() {
  const response = await fetch(`${API_BASE}/api/conversations`)
  if (!response.ok) throw new Error('Failed to fetch conversations')
  return response.json()
}

export async function createConversation(title = 'New Conversation', agentType = 'react') {
  const response = await fetch(`${API_BASE}/api/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, agent_type: agentType })
  })
  if (!response.ok) throw new Error('Failed to create conversation')
  return response.json()
}

export async function getConversation(id) {
  const response = await fetch(`${API_BASE}/api/conversations/${id}`)
  if (!response.ok) throw new Error('Failed to fetch conversation')
  return response.json()
}

export async function updateConversation(id, data) {
  const response = await fetch(`${API_BASE}/api/conversations/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Failed to update conversation')
  return response.json()
}

export async function deleteConversation(id) {
  const response = await fetch(`${API_BASE}/api/conversations/${id}`, {
    method: 'DELETE'
  })
  if (!response.ok) throw new Error('Failed to delete conversation')
  return response.json()
}

export async function addMessage(conversationId, role, content, thinking = null) {
  const response = await fetch(`${API_BASE}/api/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role, content, thinking })
  })
  if (!response.ok) throw new Error('Failed to add message')
  return response.json()
}
```

- [ ] **Step 2: Commit**

```bash
git add src/frontend/src/api.js
git commit -m "feat: add conversation API functions to frontend client"
```

---

## Task 8: Integrate Persistence in App.vue

**Files:**
- Modify: `src/frontend/src/App.vue`

- [ ] **Step 1: Update App.vue with persistence logic**

Key changes:
1. Load conversations on mount
2. Create new conversation when starting fresh
3. Save messages after each exchange
4. Load conversation when selecting from history

```javascript
// Add to imports
import { getConversations, createConversation, getConversation, deleteConversation, addMessage, updateConversation } from './api.js'

// Add conversation ID state
const currentConversationId = ref(null)

// Update newConversation function
async function newConversation() {
  messages.value = []
  currentResponse.value = ''
  currentThinking.value = ''
  currentConversationId.value = null
}

// Update selectConversation function
async function selectConversation(id) {
  activeConversationId.value = id
  currentConversationId.value = id

  try {
    const conv = await getConversation(id)
    messages.value = conv.messages.map(m => ({
      type: m.role === 'user' ? 'user' : conv.agent_type,
      content: m.content,
      thinking: m.thinking
    }))
    currentAgent.value = conv.agent_type
  } catch (e) {
    console.error('Failed to load conversation:', e)
  }
}

// Update sendMessage to save messages
async function sendMessage(content) {
  if (!content || !ws) return

  // Create conversation if needed
  if (!currentConversationId.value) {
    try {
      const conv = await createConversation(content.slice(0, 50), currentAgent.value)
      currentConversationId.value = conv.id
      await loadConversations()
    } catch (e) {
      console.error('Failed to create conversation:', e)
    }
  }

  // Save user message
  messages.value.push({ type: 'user', content })

  if (currentConversationId.value) {
    try {
      await addMessage(currentConversationId.value, 'user', content)
    } catch (e) {
      console.error('Failed to save user message:', e)
    }
  }

  currentResponse.value = ''
  currentThinking.value = ''
  isGenerating.value = true

  ws.send(content, currentAgent.value)
}

// Add function to load conversations
async function loadConversations() {
  try {
    const convs = await getConversations()
    // Group by date for sidebar
    conversations.value = convs.map(c => ({
      id: c.id,
      title: c.title,
      date: new Date(c.updated_at).toLocaleDateString()
    }))
  } catch (e) {
    console.error('Failed to load conversations:', e)
  }
}

// Update handleMessage to save assistant message
async function handleMessage(data) {
  if (data.type === 'token') {
    currentResponse.value += data.data.content
  } else if (data.type === 'thinking') {
    if (currentThinking.value) {
      currentThinking.value += '\n' + data.data.content
    } else {
      currentThinking.value = data.data.content
    }
  } else if (data.type === 'done') {
    if (currentResponse.value) {
      const thinking = currentThinking.value || null
      messages.value.push({
        type: currentAgent.value,
        content: currentResponse.value,
        thinking
      })

      // Save assistant message
      if (currentConversationId.value) {
        try {
          await addMessage(currentConversationId.value, 'assistant', currentResponse.value, thinking)
          await loadConversations() // Refresh sidebar
        } catch (e) {
          console.error('Failed to save assistant message:', e)
        }
      }

      currentResponse.value = ''
      currentThinking.value = ''
    }
    isGenerating.value = false
  } else if (data.type === 'error') {
    messages.value.push({
      type: 'agent',
      content: `Error: ${data.data.message}`,
      thinking: null
    })
    isGenerating.value = false
    currentResponse.value = ''
    currentThinking.value = ''
  }
}

// Load conversations on mount
onMounted(async () => {
  document.documentElement.setAttribute('data-theme', theme.value)

  // Load agents
  try {
    const agents = await getAgents()
    agentOptions.value = agents.map(a => ({
      id: a.id,
      label: a.name
    }))
  } catch (e) {
    console.error('Failed to load agents:', e)
  }

  // Load conversations
  await loadConversations()

  // Connect WebSocket
  connectWebSocket()
})
```

- [ ] **Step 2: Commit**

```bash
git add src/frontend/src/App.vue
git commit -m "feat: integrate conversation persistence in App.vue"
```

---

## Task 9: Test the Implementation

- [ ] **Step 1: Start the backend server**

Run: `uv run uvicorn src.backend.main:app --reload`
Expected: Server starts with database initialization

- [ ] **Step 2: Start the frontend**

Run: `cd src/frontend && npm run dev`
Expected: Frontend starts

- [ ] **Step 3: Test conversation flow**

Manual test:
1. Send a message - should create new conversation
2. Send another message - should be saved to same conversation
3. Click "New Chat" - should clear and allow new conversation
4. Check sidebar - should show conversation history
5. Click a conversation in history - should load messages
6. Refresh page - conversations should persist

- [ ] **Step 4: Verify database file**

Run: `ls -la conversations.db`
Expected: SQLite database file created

---

## Task 10: Final Commit

- [ ] **Step 1: Final commit for feature completion**

```bash
git add -A
git commit -m "feat: add conversation history persistence with SQLite

- Add SQLAlchemy async models for Conversation and Message
- Create CRUD API endpoints for conversation management
- Integrate persistence in frontend App.vue
- Auto-save messages during chat
- Load conversation history on app startup"
```

---

## Summary

This implementation adds:

1. **SQLite database** with async SQLAlchemy ORM
2. **Conversation model** with title, agent_type, timestamps
3. **Message model** with role, content, thinking, timestamps
4. **REST API endpoints** for full conversation CRUD
5. **Frontend integration** to auto-save and load conversations
6. **Sidebar history** populated from database

The user can now:
- Create new conversations
- Have messages auto-saved
- View conversation history in sidebar
- Load previous conversations
- Delete old conversations