# Claude-Style Chat Interface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the existing basic chat UI into a polished Claude-style interface with sidebar history, theme toggle, and improved UX.

**Architecture:** Vue 3 SPA with CSS variables for theming. Sidebar component for navigation/history, main area for messages, top bar for agent tabs, fixed bottom input. Theme state managed in localStorage.

**Tech Stack:** Vue 3 (Composition API), Ant Design Vue, CSS variables, localStorage

---

## File Structure

```
src/frontend/src/
├── App.vue                    -- Main layout (rewrite)
├── components/
│   ├── Sidebar.vue            -- Logo, theme toggle, history (create)
│   ├── TopBar.vue             -- Agent selector tabs (create)
│   ├── MessageList.vue        -- Conversation messages (create)
│   └── InputArea.vue          -- Multi-line input (create)
├── style.css                  -- CSS variables, global styles (rewrite)
├── api.js                     -- No changes
└── main.js                    -- No changes
```

---

### Task 1: CSS Variables and Theme System

**Files:**
- Rewrite: `src/frontend/src/style.css`

- [ ] **Step 1: Replace style.css with CSS variables for theming**

Write the complete new style.css:

```css
/* CSS Variables for theming */
:root {
  --sidebar-bg: #1a1a1a;
  --main-bg: #212121;
  --card-bg: #2a2a2a;
  --input-bg: #333333;
  --text-primary: #ffffff;
  --text-secondary: #888888;
  --accent: #d4a574;
  --accent-hover: #e0b68a;
  --border: #444444;
  --hover-bg: #333333;
}

[data-theme="light"] {
  --sidebar-bg: #f9f9f9;
  --main-bg: #ffffff;
  --card-bg: #f5f5f5;
  --input-bg: #f0f0f0;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --accent: #8b5cf6;
  --accent-hover: #a78bfa;
  --border: #e5e5e5;
  --hover-bg: #f0f0f0;
}

/* Reset and base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--main-bg);
  color: var(--text-primary);
  font-size: 15px;
  line-height: 1.6;
}

/* App layout */
.app-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
}

.sidebar-logo {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.theme-toggle {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-primary);
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
}

.theme-toggle:hover {
  background: var(--hover-bg);
}

.new-chat-btn {
  margin: 12px 16px;
  padding: 10px 16px;
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text-primary);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  text-align: left;
}

.new-chat-btn:hover {
  background: var(--hover-bg);
}

.history-section {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.history-date {
  font-size: 12px;
  color: var(--text-secondary);
  padding: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.history-item {
  padding: 10px 12px;
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-item:hover {
  background: var(--hover-bg);
  color: var(--text-primary);
}

.history-item.active {
  background: var(--hover-bg);
  color: var(--text-primary);
}

/* Main area */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--main-bg);
  min-width: 0;
}

/* Top bar */
.top-bar {
  padding: 12px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.agent-tabs {
  display: flex;
  gap: 8px;
}

.agent-tab {
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
}

.agent-tab:hover {
  color: var(--text-primary);
  border-color: var(--text-secondary);
}

.agent-tab.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #000;
}

.new-chat-top {
  padding: 6px 14px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 12px;
}

.new-chat-top:hover {
  color: var(--text-primary);
}

/* Message list */
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.message-container {
  max-width: 768px;
  width: 100%;
}

.message {
  margin-bottom: 24px;
}

.message-user {
  text-align: left;
}

.message-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.message-content {
  color: var(--text-primary);
  line-height: 1.7;
}

.message-agent {
  background: var(--card-bg);
  padding: 16px;
  border-radius: 12px;
  border-left: 3px solid var(--accent);
}

.message-agent .message-label {
  color: var(--accent);
}

.message-thinking {
  background: var(--card-bg);
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  font-style: italic;
  margin-bottom: 16px;
}

.empty-hint {
  color: var(--text-secondary);
  text-align: center;
  padding: 100px 20px;
  font-size: 15px;
}

.cursor-blink {
  display: inline-block;
  animation: blink 1s infinite;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Input area */
.input-area {
  padding: 16px 24px 24px;
  display: flex;
  justify-content: center;
  border-top: 1px solid var(--border);
}

.input-container {
  max-width: 768px;
  width: 100%;
  background: var(--input-bg);
  border-radius: 16px;
  padding: 12px;
}

.input-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.action-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  padding: 6px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 18px;
}

.action-btn:hover {
  color: var(--text-primary);
  background: var(--hover-bg);
}

.input-row {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.input-textarea {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: 15px;
  font-family: inherit;
  line-height: 1.5;
  resize: none;
  outline: none;
  min-height: 24px;
  max-height: 120px;
}

.input-textarea::placeholder {
  color: var(--text-secondary);
}

.send-btn {
  background: var(--accent);
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  color: #000;
  font-weight: 500;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: var(--accent-hover);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stop-btn {
  background: #ef4444;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  color: #fff;
  font-weight: 500;
  cursor: pointer;
  font-size: 14px;
}

.stop-btn:hover {
  background: #dc2626;
}

/* Connection status */
.connection-status {
  text-align: center;
  color: var(--text-secondary);
  font-size: 12px;
  padding: 8px;
}

/* Scrollbar styling */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}
```

- [ ] **Step 2: Verify CSS loads correctly**

Run: Open browser at http://localhost:3000 (after frontend starts)
Expected: Page should load with dark theme colors applied (but layout may be broken until components are updated)

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/style.css
git commit -m "style: add CSS variables and Claude-style theme system"
```

---

### Task 2: Create Sidebar Component

**Files:**
- Create: `src/frontend/src/components/Sidebar.vue`

- [ ] **Step 1: Create components directory**

```bash
mkdir -p src/frontend/src/components
```

- [ ] **Step 2: Write Sidebar.vue component**

```vue
<template>
  <div class="sidebar">
    <!-- Header with logo and theme toggle -->
    <div class="sidebar-header">
      <div class="sidebar-logo">myHelloAgent</div>
      <button class="theme-toggle" @click="$emit('toggle-theme')" :title="theme === 'dark' ? 'Switch to light' : 'Switch to dark'">
        {{ theme === 'dark' ? '☀️' : '🌙' }}
      </button>
    </div>

    <!-- New Chat button -->
    <button class="new-chat-btn" @click="$emit('new-chat')">
      + New Chat
    </button>

    <!-- Conversation History -->
    <div class="history-section">
      <div v-for="group in historyGroups" :key="group.date">
        <div class="history-date">{{ group.date }}</div>
        <div
          v-for="conv in group.conversations"
          :key="conv.id"
          :class="['history-item', { active: conv.id === activeId }]"
          @click="$emit('select-conversation', conv.id)"
        >
          {{ conv.title }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  theme: {
    type: String,
    default: 'dark'
  },
  conversations: {
    type: Array,
    default: () => []
  },
  activeId: {
    type: [String, Number],
    default: null
  }
})

defineEmits(['toggle-theme', 'new-chat', 'select-conversation'])

// Group conversations by date
const historyGroups = computed(() => {
  // For now, return mock data - in future this will be real data
  if (props.conversations.length === 0) {
    return []
  }

  // Group by date label (Today, Yesterday, etc.)
  const groups = {}
  props.conversations.forEach(conv => {
    const dateLabel = conv.dateLabel || 'Earlier'
    if (!groups[dateLabel]) {
      groups[dateLabel] = []
    }
    groups[dateLabel].push(conv)
  })

  return Object.entries(groups).map(([date, conversations]) => ({
    date,
    conversations
  }))
})
</script>
```

- [ ] **Step 3: Verify component file exists**

Run: `ls -la src/frontend/src/components/`
Expected: Sidebar.vue file exists

- [ ] **Step 4: Commit**

```bash
git add src/frontend/src/components/Sidebar.vue
git commit -m "feat: add Sidebar component with theme toggle and history"
```

---

### Task 3: Create TopBar Component

**Files:**
- Create: `src/frontend/src/components/TopBar.vue`

- [ ] **Step 1: Write TopBar.vue component**

```vue
<template>
  <div class="top-bar">
    <div class="agent-tabs">
      <button
        v-for="agent in agents"
        :key="agent.id"
        :class="['agent-tab', { active: currentAgent === agent.id }]"
        @click="$emit('select-agent', agent.id)"
      >
        {{ agent.label }}
      </button>
    </div>
    <button class="new-chat-top" @click="$emit('new-chat')">
      New Chat
    </button>
  </div>
</template>

<script setup>
defineProps({
  agents: {
    type: Array,
    default: () => [
      { id: 'react', label: 'ReAct Agent' },
      { id: 'reflection', label: 'Reflection' },
      { id: 'plan', label: 'Plan' }
    ]
  },
  currentAgent: {
    type: String,
    default: 'react'
  }
})

defineEmits(['select-agent', 'new-chat'])
</script>
```

- [ ] **Step 2: Verify component file exists**

Run: `ls -la src/frontend/src/components/`
Expected: TopBar.vue file exists

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/components/TopBar.vue
git commit -m "feat: add TopBar component with agent selector tabs"
```

---

### Task 4: Create MessageList Component

**Files:**
- Create: `src/frontend/src/components/MessageList.vue`

- [ ] **Step 1: Write MessageList.vue component**

```vue
<template>
  <div class="message-list" ref="listRef">
    <div class="message-container">
      <!-- Empty state -->
      <div v-if="messages.length === 0 && !isGenerating" class="empty-hint">
        Start a conversation! Select an Agent type and send a message.
      </div>

      <!-- Messages -->
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.type === 'user' ? 'message-user' : 'message-agent']"
      >
        <!-- Thinking message -->
        <div v-if="msg.type === 'thinking'" class="message-thinking">
          {{ msg.content }}
        </div>

        <!-- User message -->
        <div v-else-if="msg.type === 'user'">
          <div class="message-label">You</div>
          <div class="message-content">{{ msg.content }}</div>
        </div>

        <!-- Agent message -->
        <div v-else>
          <div class="message-label">{{ getAgentLabel(msg.type) }}</div>
          <div class="message-content">{{ msg.content }}</div>
        </div>
      </div>

      <!-- Streaming response -->
      <div v-if="isGenerating && currentResponse" class="message message-agent">
        <div class="message-label">Agent</div>
        <div class="message-content">
          {{ currentResponse }}<span class="cursor-blink">|</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  isGenerating: {
    type: Boolean,
    default: false
  },
  currentResponse: {
    type: String,
    default: ''
  }
})

const listRef = ref(null)

// Agent label mapping
const agentLabels = {
  agent: 'Agent',
  react: 'ReAct Agent',
  reflection: 'Reflection Agent',
  plan: 'Plan Agent'
}

function getAgentLabel(type) {
  return agentLabels[type] || 'Agent'
}

// Auto-scroll to bottom when new content arrives
watch([() => props.messages.length, () => props.currentResponse], () => {
  nextTick(() => {
    if (listRef.value) {
      listRef.value.scrollTop = listRef.value.scrollHeight
    }
  })
})
</script>
```

- [ ] **Step 2: Verify component file exists**

Run: `ls -la src/frontend/src/components/`
Expected: MessageList.vue file exists

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/components/MessageList.vue
git commit -m "feat: add MessageList component with Claude-style cards"
```

---

### Task 5: Create InputArea Component

**Files:**
- Create: `src/frontend/src/components/InputArea.vue`

- [ ] **Step 1: Write InputArea.vue component**

```vue
<template>
  <div class="input-area">
    <div class="input-container">
      <!-- Action buttons -->
      <div class="input-actions">
        <button class="action-btn" title="Attach file (coming soon)">
          📎
        </button>
        <button class="action-btn" title="Voice input (coming soon)">
          🎤
        </button>
      </div>

      <!-- Input row -->
      <div class="input-row">
        <textarea
          ref="textareaRef"
          v-model="inputText"
          class="input-textarea"
          placeholder="Message myHelloAgent..."
          :disabled="disabled || !isConnected"
          @keydown="handleKeydown"
          @input="autoResize"
        ></textarea>

        <!-- Send button -->
        <button
          v-if="!isGenerating"
          class="send-btn"
          :disabled="!inputText.trim() || !isConnected || disabled"
          @click="sendMessage"
        >
          Send
        </button>

        <!-- Stop button -->
        <button
          v-else
          class="stop-btn"
          @click="$emit('interrupt')"
        >
          Stop
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  isConnected: {
    type: Boolean,
    default: false
  },
  isGenerating: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send', 'interrupt'])

const inputText = ref('')
const textareaRef = ref(null)

// Auto-resize textarea
function autoResize() {
  const textarea = textareaRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
  }
}

// Handle keyboard shortcuts
function handleKeydown(event) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    sendMessage()
  }
}

// Send message
function sendMessage() {
  const text = inputText.value.trim()
  if (text && props.isConnected && !props.disabled) {
    emit('send', text)
    inputText.value = ''
    // Reset textarea height
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  }
}

// Expose for parent to clear if needed
defineExpose({
  clear: () => {
    inputText.value = ''
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  }
})
</script>
```

- [ ] **Step 2: Verify component file exists**

Run: `ls -la src/frontend/src/components/`
Expected: InputArea.vue file exists

- [ ] **Step 3: Commit**

```bash
git add src/frontend/src/components/InputArea.vue
git commit -m "feat: add InputArea component with multi-line support"
```

---

### Task 6: Refactor App.vue with New Components

**Files:**
- Rewrite: `src/frontend/src/App.vue`

- [ ] **Step 1: Rewrite App.vue to use new components**

```vue
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
    messages.value.push({
      type: 'thinking',
      content: data.data.content
    })
  } else if (data.type === 'done') {
    if (currentResponse.value) {
      messages.value.push({
        type: currentAgent.value,
        content: currentResponse.value
      })
      currentResponse.value = ''
    }
    isGenerating.value = false
  } else if (data.type === 'error') {
    messages.value.push({
      type: 'agent',
      content: `Error: ${data.data.message}`
    })
    isGenerating.value = false
    currentResponse.value = ''
  }
}

// Send message
function sendMessage(content) {
  if (!content || !ws) return

  messages.value.push({ type: 'user', content })
  currentResponse.value = ''
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
```

- [ ] **Step 2: Verify frontend builds and runs**

Run: Start frontend dev server (if not running) and check http://localhost:3000
Expected: New Claude-style layout appears with sidebar, top bar, message area, and input

- [ ] **Step 3: Test theme toggle**

Action: Click the theme toggle button (☀️/🌙) in sidebar
Expected: Theme switches between dark and light, preference saved to localStorage

- [ ] **Step 4: Test agent tabs**

Action: Click different agent tabs (ReAct Agent, Reflection, Plan)
Expected: Active tab changes to accent color

- [ ] **Step 5: Test message sending**

Action: Type a message and click Send or press Enter
Expected: Message appears in chat, agent responds with streaming

- [ ] **Step 6: Commit**

```bash
git add src/frontend/src/App.vue
git commit -m "feat: integrate all components into Claude-style layout"
```

---

### Task 7: Final Testing and Polish

**Files:**
- None (testing only)

- [ ] **Step 1: Verify all features work**

Test each feature:
1. Theme toggle: Dark/light switch persists across page refresh
2. Agent tabs: Clicking tabs changes active agent
3. Message display: User and agent messages display correctly
4. Streaming: Agent response streams with cursor animation
5. Input: Auto-expand textarea, Enter to send, Shift+Enter for newline
6. Stop button: Appears during generation, interrupts when clicked
7. New chat: Clears conversation
8. Connection status: Shows connected/disconnected state

- [ ] **Step 2: Final commit**

```bash
git add -A
git commit -m "feat: complete Claude-style chat UI implementation"
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | CSS variables and theme system | style.css |
| 2 | Sidebar component | Sidebar.vue |
| 3 | TopBar component | TopBar.vue |
| 4 | MessageList component | MessageList.vue |
| 5 | InputArea component | InputArea.vue |
| 6 | Refactor App.vue | App.vue |
| 7 | Final testing | - |

## Estimated Commits: 7