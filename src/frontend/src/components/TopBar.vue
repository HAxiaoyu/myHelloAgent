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