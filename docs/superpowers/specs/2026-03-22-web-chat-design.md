# Web Chat Application Design

## Overview

Build a web-based chat application for the existing LLM Agent system, supporting three agent modes (ReAct, Reflection, Plan-and-Solve) with real-time streaming via WebSocket.

## Architecture

```
src/
├── core/                    # Existing Agent implementations
│   ├── __init__.py
│   ├── llm_client.py
│   ├── react_agent.py
│   ├── reflection_agent.py
│   ├── plan_agent.py
│   ├── tools.py
│   └── memory.py
│
├── backend/                 # FastAPI service
│   ├── main.py
│   ├── routers/
│   │   └── chat.py
│   ├── services/
│   │   └── agent_service.py
│   └── models/
│       └── schemas.py
│
└── frontend/                # Vue 3 application
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── style.css
        └── api.js
```

## Technology Stack

### Backend
- FastAPI 0.115+
- Pydantic v2
- Uvicorn 0.30+
- WebSocket (built-in)

### Frontend
- Vue 3 + JavaScript
- Vite 5
- Ant Design Vue 4.2
- Native WebSocket API

## API Design

### REST Endpoints

| Route | Method | Description |
|-------|--------|-------------|
| `GET /api/agents` | GET | Get available agent list |
| `GET /api/tools` | GET | Get tool status |
| `POST /api/chat/new` | POST | Start new conversation |

### WebSocket Endpoint

**Route**: `WS /api/ws/chat`

#### Client → Server Messages

```json
// Send message
{"type": "message", "data": {"content": "你好", "agent_type": "react"}}

// Interrupt generation
{"type": "interrupt"}
```

#### Server → Client Messages

```json
// Streaming token
{"type": "token", "data": {"content": "你"}}

// Thinking process
{"type": "thinking", "data": {"content": "正在搜索..."}}

// Complete
{"type": "done", "data": {"message": "完成"}}

// Error
{"type": "error", "data": {"message": "错误信息"}}
```

## Data Models

```python
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
```

## Frontend Components

### Layout
```
┌─────────────────────────────────────────────────┐
│  Header: myHelloAgent  │ [Agent选择器] [新建对话] │
├─────────────────────────────────────────────────┤
│              消息列表区域                         │
├─────────────────────────────────────────────────┤
│  工具状态: Search ✓                              │
├─────────────────────────────────────────────────┤
│  输入框 + 发送按钮                                │
└─────────────────────────────────────────────────┘
```

### Ant Design Vue Components

| Feature | Component |
|---------|-----------|
| Agent selector | `a-select` |
| Message list | `a-card` + `a-typography` |
| Input | `a-input` + `a-button` |
| Tool status | `a-tag` |
| Layout | `a-layout` |

## Error Handling

| Scenario | Handling |
|----------|----------|
| WebSocket disconnect | Show reconnect button |
| LLM API timeout | Return error, prompt retry |
| Agent execution failure | Return error, keep history |
| Tool call failure | Agent continues or returns error |

## Session Management

- In-memory storage (no database for MVP)
- Each WebSocket connection is independent
- "New conversation" clears history

## Dependencies

### Backend (pyproject.toml)
```
fastapi>=0.115.0
uvicorn>=0.30.0
websockets>=12.0
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "vue": "^3.4",
    "ant-design-vue": "^4.2"
  },
  "devDependencies": {
    "vite": "^5.0",
    "@vitejs/plugin-vue": "^5.0"
  }
}
```

## Migration Plan

1. Move existing files to `src/core/`
2. Create backend FastAPI service
3. Create frontend Vue application
4. Integrate and test