<template>
  <div class="chat-container">
    <!-- Header -->
    <div class="header">
      <h2>myHelloAgent</h2>
      <div>
        <a-select
          v-model:value="currentAgent"
          style="width: 200px; margin-right: 12px"
          :options="agentOptions"
        />
        <a-button @click="newConversation">新建对话</a-button>
      </div>
    </div>

    <!-- Tool Status -->
    <div class="tool-status">
      <span>工具状态: </span>
      <a-tag v-for="tool in tools" :key="tool.name" :color="tool.available ? 'green' : 'red'">
        {{ tool.name }}
      </a-tag>
    </div>

    <!-- Message List -->
    <div class="message-list" ref="messageList">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.type === 'user' ? 'message-user' : 'message-agent']"
      >
        <div v-if="msg.type === 'thinking'" class="message-thinking">
          {{ msg.content }}
        </div>
        <div v-else>
          <strong>{{ msg.type === 'user' ? '我' : 'Agent' }}:</strong>
          {{ msg.content }}
        </div>
      </div>
      <div v-if="isGenerating" class="message message-agent">
        <strong>Agent:</strong> {{ currentResponse }}
      </div>
    </div>

    <!-- Input -->
    <div class="input-area">
      <a-input
        v-model:value="inputMessage"
        placeholder="输入消息..."
        @pressEnter="sendMessage"
        :disabled="!isConnected || isGenerating"
      />
      <a-button
        type="primary"
        @click="sendMessage"
        :disabled="!inputMessage.trim() || !isConnected || isGenerating"
      >
        发送
      </a-button>
      <a-button
        v-if="isGenerating"
        danger
        @click="interrupt"
      >
        停止
      </a-button>
    </div>

    <!-- Connection Status -->
    <div style="margin-top: 12px; text-align: center; color: #999">
      {{ isConnected ? '已连接' : '未连接' }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { getAgents, getTools, createChatSocket } from './api.js'

const messages = ref([])
const inputMessage = ref('')
const currentAgent = ref('react')
const agents = ref([])
const tools = ref([])
const isConnected = ref(false)
const isGenerating = ref(false)
const currentResponse = ref('')
const messageList = ref(null)

let ws = null

const agentOptions = ref([])

onMounted(async () => {
  // Load agents and tools
  agents.value = await getAgents()
  tools.value = await getTools()

  agentOptions.value = agents.value.map(a => ({
    value: a.id,
    label: a.name
  }))

  // Connect WebSocket
  connectWebSocket()
})

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

function handleMessage(data) {
  if (data.type === 'token') {
    currentResponse.value += data.data.content
    scrollToBottom()
  } else if (data.type === 'thinking') {
    messages.value.push({
      type: 'thinking',
      content: data.data.content
    })
    scrollToBottom()
  } else if (data.type === 'done') {
    if (currentResponse.value) {
      messages.value.push({
        type: 'agent',
        content: currentResponse.value
      })
      currentResponse.value = ''
    }
    isGenerating.value = false
  } else if (data.type === 'error') {
    messages.value.push({
      type: 'agent',
      content: `错误: ${data.data.message}`
    })
    isGenerating.value = false
    currentResponse.value = ''
  }
}

function sendMessage() {
  if (!inputMessage.value.trim() || !ws) return

  const content = inputMessage.value.trim()
  messages.value.push({ type: 'user', content })
  inputMessage.value = ''
  currentResponse.value = ''
  isGenerating.value = true

  ws.send(content, currentAgent.value)
  scrollToBottom()
}

function interrupt() {
  if (ws) {
    ws.interrupt()
    isGenerating.value = false
  }
}

function newConversation() {
  messages.value = []
  currentResponse.value = ''
}

function scrollToBottom() {
  nextTick(() => {
    if (messageList.value) {
      messageList.value.scrollTop = messageList.value.scrollHeight
    }
  })
}
</script>