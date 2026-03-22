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