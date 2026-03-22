# Claude-Style Chat Interface Design Spec

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the existing basic chat UI into a polished Claude-style interface with sidebar history, theme toggle, and improved UX.

**Architecture:** Vue 3 SPA with CSS variables for theming. Sidebar component for navigation/history, main area for messages, top bar for agent tabs, fixed bottom input. Theme state managed in localStorage.

**Tech Stack:** Vue 3 (Composition API), Ant Design Vue, CSS variables, localStorage

---

## Components Structure

```
App.vue
├── Sidebar.vue          -- Logo, theme toggle, new chat, history list
├── MainArea.vue
│   ├── TopBar.vue       -- Agent selector tabs
│   ├── MessageList.vue  -- Conversation messages
│   └── InputArea.vue    -- Multi-line input with actions
```

---

## Visual Design

### Layout Dimensions
- Sidebar: 260px fixed width
- Main area: fills remaining space
- Message container: max-width 768px, centered
- Input area: max-width 768px, centered, 24px bottom padding

### Dark Theme Colors
| Element | Color |
|---------|-------|
| Sidebar background | `#1a1a1a` |
| Main background | `#212121` |
| Message card background | `#2a2a2a` |
| Input background | `#333333` |
| Primary text | `#ffffff` |
| Secondary text | `#888888` |
| Accent (buttons, highlights) | `#d4a574` |
| Border | `#444444` |

### Light Theme Colors
| Element | Color |
|---------|-------|
| Sidebar background | `#f9f9f9` |
| Main background | `#ffffff` |
| Message card background | `#f5f5f5` |
| Input background | `#f0f0f0` |
| Primary text | `#1a1a1a` |
| Secondary text | `#666666` |
| Accent (buttons, highlights) | `#8b5cf6` |
| Border | `#e5e5e5` |

### Typography
- Font: System stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`)
- Message text: 15px, line-height 1.6
- Labels (You, Agent names): 12px, uppercase or capitalized
- Sidebar items: 13px
- Input: 15px

---

## Component Specifications

### 1. Sidebar.vue

**Purpose:** Navigation, conversation history, theme toggle

**Structure:**
```
┌─────────────────────────┐
│ myHelloAgent    [🌙/☀️] │  <- Header with theme toggle
├─────────────────────────┤
│ [+ New Chat]            │  <- Action button
├─────────────────────────┤
│ Today                   │  <- Date group
│   > Chat title 1        │  <- Active (highlighted)
│   > Chat title 2        │
│ Yesterday               │
│   > Chat title 3        │
└─────────────────────────┘
```

**Behavior:**
- Theme toggle: Click to switch dark/light, save to localStorage
- New Chat: Clear current conversation, start fresh
- History item click: Load that conversation
- Active conversation: highlighted with accent background

**Props:** None (uses global state)

**Emits:** `new-chat`, `select-conversation(id)`, `toggle-theme`

### 2. TopBar.vue

**Purpose:** Agent type selector tabs

**Structure:**
```
┌─────────────────────────────────────────────────┐
│ [ReAct Agent]  [Reflection]  [Plan]    [New]   │
└─────────────────────────────────────────────────┘
```

**Behavior:**
- Click tab to switch agent type
- Active tab: accent background, accent text
- Inactive tab: transparent background, border, muted text
- "New" button on right: start new conversation

**Props:** `currentAgent: string`

**Emits:** `select-agent(type)`, `new-chat`

### 3. MessageList.vue

**Purpose:** Display conversation messages

**Structure:**
```
┌─────────────────────────────────────┐
│                                     │
│  YOU                                │
│  What is ReAct agent?               │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ REACT AGENT                 │   │
│  │ ReAct stands for Reasoning  │   │
│  │ and Acting. It alternates   │   │
│  │ between thinking and doing. │   │
│  └─────────────────────────────┘   │
│                                     │
│  [Thinking: Searching web...]       │  <- Optional thinking indicator
│                                     │
└─────────────────────────────────────┘
```

**Message Types:**
1. User message: Simple text, right-aligned label "You"
2. Agent message: Card with background, accent-colored label
3. Thinking message: Smaller, muted, italic

**Behavior:**
- Auto-scroll to bottom on new message
- Streaming text shows cursor animation
- Empty state: Centered hint text

**Props:** `messages: Array`, `isGenerating: boolean`, `currentResponse: string`

### 4. InputArea.vue

**Purpose:** Message input with actions

**Structure:**
```
┌─────────────────────────────────────────┐
│  📎  🎤                                 │  <- Action buttons
│  ┌─────────────────────────────────┐   │
│  │ Type a message...               │ ↑ │  <- Textarea + send
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Behavior:**
- Textarea auto-expands (min 24px, max 120px)
- Attachment button: placeholder (no functionality yet)
- Mic button: placeholder (no functionality yet)
- Send button: enabled only when text is non-empty
- Enter to send, Shift+Enter for newline

**Props:** `disabled: boolean`, `isConnected: boolean`

**Emits:** `send(message)`, `interrupt`

---

## State Management

### Theme State
```javascript
// Stored in localStorage
const theme = ref(localStorage.getItem('theme') || 'dark')

// CSS variables applied to :root
function applyTheme(theme) {
  const colors = theme === 'dark' ? darkColors : lightColors
  Object.entries(colors).forEach(([key, value]) => {
    document.documentElement.style.setProperty(`--${key}`, value)
  })
}
```

### Conversation State
```javascript
// Current conversation
const messages = ref([])
const currentAgent = ref('react')
const isGenerating = ref(false)
const currentResponse = ref('')

// History (future: persist to localStorage or backend)
const conversations = ref([])
const activeConversationId = ref(null)
```

---

## CSS Variables Approach

Define all colors as CSS variables for easy theme switching:

```css
:root {
  --sidebar-bg: #1a1a1a;
  --main-bg: #212121;
  --card-bg: #2a2a2a;
  --input-bg: #333333;
  --text-primary: #ffffff;
  --text-secondary: #888888;
  --accent: #d4a574;
  --border: #444444;
}

[data-theme="light"] {
  --sidebar-bg: #f9f9f9;
  --main-bg: #ffffff;
  --card-bg: #f5f5f5;
  --input-bg: #f0f0f0;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --accent: #8b5cf6;
  --border: #e5e5e5;
}
```

---

## Files to Modify/Create

| File | Action | Description |
|------|--------|-------------|
| `src/frontend/src/App.vue` | Rewrite | Split into component architecture |
| `src/frontend/src/components/Sidebar.vue` | Create | New sidebar component |
| `src/frontend/src/components/TopBar.vue` | Create | Agent tabs component |
| `src/frontend/src/components/MessageList.vue` | Create | Message display component |
| `src/frontend/src/components/InputArea.vue` | Create | Input with actions |
| `src/frontend/src/style.css` | Rewrite | CSS variables, new styles |
| `src/frontend/src/api.js` | Keep | No changes needed |

---

## Acceptance Criteria

1. **Layout**: Sidebar (260px) + main area, responsive on smaller screens
2. **Theme Toggle**: Dark/light switch, persists across sessions
3. **Agent Selector**: Top bar tabs, switches agent type correctly
4. **Message Display**: Clean Claude-style cards, streaming works
5. **Input Area**: Multi-line, auto-expand, action buttons visible
6. **History Sidebar**: Shows conversation list, click to load
7. **WebSocket**: Existing streaming functionality preserved

---

## Out of Scope

- Backend changes (API stays the same)
- Actual file attachment functionality (UI only)
- Voice input functionality (UI only)
- Conversation persistence (localStorage or backend)
- Mobile responsive design (< 768px)