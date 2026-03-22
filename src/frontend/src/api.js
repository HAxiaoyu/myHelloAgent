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

// Conversation API
export async function getConversations() {
  const response = await fetch(`${API_BASE}/conversations`)
  if (!response.ok) throw new Error('Failed to fetch conversations')
  return response.json()
}

export async function createConversation(title = 'New Conversation', agentType = 'react') {
  const response = await fetch(`${API_BASE}/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, agent_type: agentType })
  })
  if (!response.ok) throw new Error('Failed to create conversation')
  return response.json()
}

export async function getConversation(id) {
  const response = await fetch(`${API_BASE}/conversations/${id}`)
  if (!response.ok) throw new Error('Failed to fetch conversation')
  return response.json()
}

export async function updateConversation(id, data) {
  const response = await fetch(`${API_BASE}/conversations/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  if (!response.ok) throw new Error('Failed to update conversation')
  return response.json()
}

export async function deleteConversation(id) {
  const response = await fetch(`${API_BASE}/conversations/${id}`, {
    method: 'DELETE'
  })
  if (!response.ok) throw new Error('Failed to delete conversation')
  return response.json()
}

export async function addMessage(conversationId, role, content, thinking = null) {
  const response = await fetch(`${API_BASE}/conversations/${conversationId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ role, content, thinking })
  })
  if (!response.ok) throw new Error('Failed to add message')
  return response.json()
}