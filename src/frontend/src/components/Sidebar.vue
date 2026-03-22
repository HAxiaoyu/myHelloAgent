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