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