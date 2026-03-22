<template>
  <div class="app-container" :data-theme="theme">
    <!-- Sidebar -->
    <Sidebar
      :theme="theme"
      :conversations="conversations"
      :active-id="activeConversationId"
      @toggle-theme="toggleTheme"
      @new-chat="newConversation"
      @select-conversation="selectConversation"
    />

    <!-- Main Area -->
    <div class="main-area">
      <!-- Top Bar with Agent Tabs -->
      <TopBar
        :agents="agentOptions"
        :current-agent="currentAgent"
        @select-agent="selectAgent"
        @new-chat="newConversation"
      />

      <!-- Message List -->
      <MessageList
        :messages="messages"
        :is-generating="isGenerating"
        :current-response="currentResponse"
        :current-thinking="currentThinking"
      />

      <!-- Input Area -->
      <InputArea
        :disabled="false"
        :is-connected="isConnected"
        :is-generating="isGenerating"
        @send="sendMessage"
        @interrupt="interrupt"
      />

      <!-- Connection Status -->
      <div class="connection-status">
        {{ isConnected ? '● Connected' : '○ Disconnected' }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import TopBar from './components/TopBar.vue'
import MessageList from './components/MessageList.vue'
import InputArea from './components/InputArea.vue'
import { getAgents, getTools, createChatSocket, getConversations, createConversation, getConversation, deleteConversation, addMessage, updateConversation } from './api.js'

// Theme state
const theme = ref(localStorage.getItem('theme') || 'dark')

// Conversation state
const messages = ref([])
const currentAgent = ref('react')
const isGenerating = ref(false)
const currentResponse = ref('')
const currentThinking = ref('') // Store thinking content temporarily

// Connection state
const isConnected = ref(false)

// Agent options (loaded from API)
const agentOptions = ref([
  { id: 'react', label: 'ReAct Agent' },
  { id: 'reflection', label: 'Reflection' },
  { id: 'plan', label: 'Plan' }
])

// History state (mock for now)
const conversations = ref([])
const activeConversationId = ref(null)
const currentConversationId = ref(null)

let ws = null

// Theme toggle
function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('theme', theme.value)
  document.documentElement.setAttribute('data-theme', theme.value)
}

// Initialize WebSocket
function connectWebSocket() {
  ws = createChatSocket({
    onOpen: () => {
      isConnected.value = true
    },
    onClose: () => {
      isConnected.value = false
    },
    onMessage: (data) => {
      handleMessage(data)
    }
  })
}

// Handle incoming WebSocket messages
async function handleMessage(data) {
  if (data.type === 'token') {
    currentResponse.value += data.data.content
  } else if (data.type === 'thinking') {
    // Accumulate thinking content with newline separator
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

// Send message
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

// Interrupt generation
function interrupt() {
  if (ws) {
    ws.interrupt()
    isGenerating.value = false
  }
}

// New conversation
async function newConversation() {
  messages.value = []
  currentResponse.value = ''
  currentThinking.value = ''
  currentConversationId.value = null
  activeConversationId.value = null
}

// Load conversations from API
async function loadConversations() {
  try {
    const convs = await getConversations()
    conversations.value = convs.map(c => ({
      id: c.id,
      title: c.title,
      date: new Date(c.updated_at).toLocaleDateString()
    }))
  } catch (e) {
    console.error('Failed to load conversations:', e)
  }
}

// Select conversation from history
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

// Select agent
function selectAgent(agentId) {
  currentAgent.value = agentId
}

onMounted(async () => {
  // Apply saved theme
  document.documentElement.setAttribute('data-theme', theme.value)

  // Load agents from API
  try {
    const agents = await getAgents()
    agentOptions.value = agents.map(a => ({
      id: a.id,
      label: a.name
    }))
  } catch (e) {
    console.error('Failed to load agents:', e)
  }

  // Load conversations from API
  await loadConversations()

  // Connect WebSocket
  connectWebSocket()
})
</script>
