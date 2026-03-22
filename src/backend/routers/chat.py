# src/backend/routers/chat.py
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..models.schemas import WSSResponse
from ..services.agent_service import AgentService

router = APIRouter(prefix="/api", tags=["chat"])

# Global agent service instance
agent_service = AgentService()

# Thread pool for running sync agent code
executor = ThreadPoolExecutor(max_workers=4)


@router.get("/agents")
async def get_agents():
    return agent_service.get_agent_list()


@router.get("/tools")
async def get_tools():
    return agent_service.get_tool_list()


@router.post("/chat/new")
async def new_chat():
    return {"message": "Conversation reset"}


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    # Capture the event loop ONCE at the start for use in thread callbacks
    loop = asyncio.get_running_loop()

    # Queue for communication between sync agent code and async WebSocket
    message_queue = asyncio.Queue()

    async def send_response(msg_type: str, data: dict):
        response = WSSResponse(type=msg_type, data=data)
        await websocket.send_json(response.model_dump())

    async def queue_sender():
        """Background task to send queued messages to WebSocket."""
        while True:
            try:
                msg = await asyncio.wait_for(message_queue.get(), timeout=0.1)
                await send_response(msg["type"], msg["data"])
            except asyncio.TimeoutError:
                continue
            except Exception:
                break

    def on_token(token: str):
        """Sync callback called from thread pool - schedules on captured loop."""
        try:
            asyncio.run_coroutine_threadsafe(
                message_queue.put({"type": "token", "data": {"content": token}}),
                loop  # Use captured loop from outer scope
            )
        except Exception:
            pass

    def on_thinking(content: str):
        """Sync callback called from thread pool - schedules on captured loop."""
        try:
            asyncio.run_coroutine_threadsafe(
                message_queue.put({"type": "thinking", "data": {"content": content}}),
                loop  # Use captured loop from outer scope
            )
        except Exception:
            pass

    # Start background sender task
    sender_task = asyncio.create_task(queue_sender())

    try:
        while True:
            raw_msg = await websocket.receive_text()
            try:
                msg = json.loads(raw_msg)

                if msg.get("type") == "message":
                    data = msg.get("data", {})
                    question = data.get("content", "")
                    agent_type = data.get("agent_type", "react")

                    if not question:
                        await send_response("error", {"message": "Empty message"})
                        continue

                    try:
                        # Run sync agent code in thread pool to avoid blocking
                        result = await loop.run_in_executor(
                            executor,
                            agent_service.run_agent_stream,
                            agent_type,
                            question,
                            on_token,
                            on_thinking,
                        )
                        await message_queue.put({"type": "done", "data": {"message": result or "完成"}})
                    except Exception as e:
                        await send_response("error", {"message": str(e)})

                elif msg.get("type") == "interrupt":
                    await send_response("done", {"message": "已中断"})

            except json.JSONDecodeError:
                await send_response("error", {"message": "Invalid JSON"})

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    finally:
        sender_task.cancel()