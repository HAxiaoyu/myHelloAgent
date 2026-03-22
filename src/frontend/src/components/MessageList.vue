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
        <!-- User message -->
        <template v-if="msg.type === 'user'">
          <div class="message-label">You</div>
          <div class="message-content">{{ msg.content }}</div>
        </template>

        <!-- Agent message -->
        <template v-else>
          <div class="message-label">{{ getAgentLabel(msg.type) }}</div>

          <!-- Collapsible thinking section -->
          <div v-if="msg.thinking" class="thinking-section">
            <div class="thinking-header" @click="toggleThinking(index)">
              <span class="thinking-icon">
                <svg :class="['chevron', { 'chevron-rotated': !expandedThinkings[index] }]" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
              </span>
              <span class="thinking-title">Thinking...</span>
            </div>
            <div v-show="expandedThinkings[index]" class="thinking-content">
              {{ msg.thinking }}
            </div>
          </div>

          <!-- Main response content -->
          <div class="message-content">{{ msg.content }}</div>
        </template>
      </div>

      <!-- Streaming response -->
      <div v-if="isGenerating && currentResponse" class="message message-agent">
        <div class="message-label">Agent</div>

        <!-- Streaming thinking -->
        <div v-if="currentThinking" class="thinking-section">
          <div class="thinking-header" @click="toggleThinking('streaming')">
            <span class="thinking-icon">
              <svg :class="['chevron', { 'chevron-rotated': !expandedThinkings['streaming'] }]" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </span>
            <span class="thinking-title">Thinking...</span>
          </div>
          <div v-show="expandedThinkings['streaming']" class="thinking-content">
            {{ currentThinking }}
          </div>
        </div>

        <div class="message-content">
          {{ currentResponse }}<span class="cursor-blink">|</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, reactive } from 'vue'

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
  },
  currentThinking: {
    type: String,
    default: ''
  }
})

const listRef = ref(null)
const expandedThinkings = reactive({})

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

function toggleThinking(index) {
  expandedThinkings[index] = !expandedThinkings[index]
}

// Auto-scroll to bottom when new content arrives
watch([() => props.messages.length, () => props.currentResponse, () => props.currentThinking], () => {
  nextTick(() => {
    if (listRef.value) {
      listRef.value.scrollTop = listRef.value.scrollHeight
    }
  })
})

// Auto-expand streaming thinking by default
watch(() => props.currentThinking, (newVal) => {
  if (newVal && expandedThinkings['streaming'] === undefined) {
    expandedThinkings['streaming'] = true
  }
})
</script>