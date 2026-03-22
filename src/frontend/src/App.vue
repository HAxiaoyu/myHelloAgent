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
import { getAgents, getTools, createChatSocket } from './api.js'

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
function handleMessage(data) {
  if (data.type === 'token') {
    currentResponse.value += data.data.content
  } else if (data.type === 'thinking') {
    // Accumulate thinking content
    currentThinking.value += data.data.content
  } else if (data.type === 'done') {
    if (currentResponse.value) {
      messages.value.push({
        type: currentAgent.value,
        content: currentResponse.value,
        thinking: currentThinking.value || null
      })
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
function sendMessage(content) {
  if (!content || !ws) return

  messages.value.push({ type: 'user', content })
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
function newConversation() {
  messages.value = []
  currentResponse.value = ''
  currentThinking.value = ''
  activeConversationId.value = null
}

// Select conversation from history
function selectConversation(id) {
  activeConversationId.value = id
  // In future, load conversation from storage
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

  // Connect WebSocket
  connectWebSocket()
})
</script>
