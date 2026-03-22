const API_BASE = '/api'

export async function getAgents() {
  const res = await fetch(`${API_BASE}/agents`)
  return res.json()
}

export async function getTools() {
  const res = await fetch(`${API_BASE}/tools`)
  return res.json()
}

export function createChatSocket({ onMessage, onOpen, onClose }) {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host
  const ws = new WebSocket(`${protocol}//${host}${API_BASE}/ws/chat`)

  ws.onopen = () => {
    console.log('WebSocket connected')
    if (onOpen) onOpen()
  }

  ws.onclose = () => {
    console.log('WebSocket disconnected')
    if (onClose) onClose()
  }

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (onMessage) onMessage(data)
  }

  ws.onerror = (error) => {
    console.error('WebSocket error:', error)
  }

  return {
    send: (content, agentType) => {
      ws.send(JSON.stringify({
        type: 'message',
        data: { content, agent_type: agentType }
      }))
    },
    interrupt: () => {
      ws.send(JSON.stringify({ type: 'interrupt' }))
    },
    close: () => ws.close()
  }
}