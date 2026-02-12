<template>
  <div class="admin-dashboard">
    <!-- Header -->
    <div class="dashboard-header">
      <h1>MayBot Admin Dashboard</h1>
      <div class="header-stats">
        <span class="stat-badge">Conversations: {{ stats.active_conversations }}</span>
        <span class="stat-badge">Messages: {{ stats.total_messages }}</span>
        <span class="stat-badge" :class="{ active: !stats.maintenance_mode }">
          Status: {{ stats.maintenance_mode ? 'Maintenance' : 'Online' }}
        </span>
      </div>
    </div>
    
    <!-- Maintenance Toggle -->
    <div class="control-panel">
      <button @click="toggleMaintenance" class="control-btn" :class="{ active: stats.maintenance_mode }">
        {{ stats.maintenance_mode ? 'Disable Maintenance' : 'Enable Maintenance' }}
      </button>
      <button @click="refreshData" class="control-btn refresh">Refresh Data</button>
      <button @click="pingServer" class="control-btn ping">Ping Server</button>
    </div>
    
    <!-- Conversations List -->
    <div class="conversations-section">
      <h2>Conversations ({{ filteredConversations.length }})</h2>
      
      <!-- Search -->
      <div class="search-box">
        <input v-model="searchQuery" placeholder="Search by name, number, persona..." @input="filterConversations" class="search-input" />
      </div>
      
      <div v-if="loading" class="loading">Loading...</div>
      <div v-else-if="filteredConversations.length === 0" class="empty">No conversations found</div>
      <div v-else class="conversation-list">
        <div 
          v-for="conv in filteredConversations" 
          :key="conv.user_number"
          class="conversation-item"
          :class="{ active: selectedConversation?.user_number === conv.user_number }"
          @click="selectConversation(conv)"
        >
          <div class="conv-main">
            <div class="conv-info">
              <strong>{{ conv.user_name || 'Unknown' }}</strong>
              <span class="conv-number">{{ conv.user_number }}</span>
            </div>
            <div class="conv-badges">
              <span class="badge-full persona">{{ getPersonaLabel(conv.persona) }}</span>
              <span class="badge-full mode">{{ getConvModeLabel(conv.convmode) }}</span>
              <span class="badge-full type">{{ getConvTypeLabel(conv.convtype) }}</span>
            </div>
          </div>
          <div class="conv-stats">
            <span>Free: {{ conv.free_tries }}</span>
            <span>Paid: {{ conv.paid_messages }}</span>
            <span>Messages: {{ conv.message_count }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Selected Conversation Details -->
    <div v-if="selectedConversation" class="details-section">
      <div class="details-header">
        <h2>Conversation Details - {{ selectedConversation.user_name || 'Unknown' }}</h2>
        <button @click="selectedConversation = null" class="close-btn">Close</button>
      </div>
      
      <!-- Basic Information -->
      <div class="detail-group">
        <h3>Basic Information</h3>
        <div class="detail-grid">
          <div class="detail-item-full">
            <label>User Number:</label>
            <span class="full-text">{{ selectedConversation.user_number }}</span>
          </div>
          <div class="detail-item-full">
            <label>User Name:</label>
            <span class="full-text">{{ selectedConversation.user_name || 'Not set' }}</span>
          </div>
          <div class="detail-item-full">
            <label>Bot Name:</label>
            <span class="full-text">{{ selectedConversation.bot_name || 'Maya' }}</span>
          </div>
        </div>
      </div>
      
      <!-- Conversation Settings -->
      <div class="detail-group">
        <h3>Conversation Settings</h3>
        <div class="detail-grid">
          <div class="detail-item-full">
            <label>Persona:</label>
            <span class="badge-large persona">{{ getPersonaLabel(selectedConversation.persona) }}</span>
          </div>
          <div class="detail-item-full">
            <label>Conversation Mode:</label>
            <span class="badge-large mode">{{ getConvModeLabel(selectedConversation.convmode) }}</span>
          </div>
          <div class="detail-item-full">
            <label>Conversation Type:</label>
            <span class="badge-large type">{{ getConvTypeLabel(selectedConversation.convtype) }}</span>
          </div>
          <div class="detail-item-full">
            <label>Script:</label>
            <span class="full-text">{{ getScriptLabel(selectedConversation.script) }}</span>
          </div>
          <div class="detail-item-full">
            <label>Interval:</label>
            <span class="full-text">{{ selectedConversation.interval || 600 }} seconds</span>
          </div>
          <div class="detail-item-full">
            <label>Temperature:</label>
            <span class="full-text">{{ selectedConversation.temperature || 0.7 }}</span>
          </div>
        </div>
      </div>
      
      <!-- Usage Limits -->
      <div class="detail-group">
        <h3>Usage Limits</h3>
        <div class="detail-grid">
          <div class="detail-item-full">
            <label>Free Tries:</label>
            <span class="full-text">{{ selectedConversation.free_tries }}</span>
          </div>
          <div class="detail-item-full">
            <label>Paid Messages:</label>
            <span class="full-text">{{ selectedConversation.paid_messages }}</span>
          </div>
          <div class="detail-item-full">
            <label>Message Count:</label>
            <span class="full-text">{{ selectedConversation.message_count }}</span>
          </div>
          <div class="detail-item-full">
            <label>Free GPT Access:</label>
            <span class="full-text">{{ selectedConversation.free_gpt ? 'Yes' : 'No' }}</span>
          </div>
          <div class="detail-item-full">
            <label>Demo User:</label>
            <span class="full-text">{{ selectedConversation.demo_user ? 'Yes' : 'No' }}</span>
          </div>
          <div class="detail-item-full">
            <label>GPT Accessed Count:</label>
            <span class="full-text">{{ selectedConversation.gpt_accessed || 0 }}</span>
          </div>
          <div class="detail-item-full">
            <label>GPT Tokens Used:</label>
            <span class="full-text">{{ selectedConversation.gpt_token_used || 0 }}</span>
          </div>
          <div class="detail-item-full">
            <label>Daily Free GPT:</label>
            <span class="full-text">{{ selectedConversation.daily_free_gpt || 5 }}</span>
          </div>
        </div>
      </div>
      
      <!-- Additional Settings -->
      <div class="detail-group">
        <h3>Additional Settings</h3>
        <div class="detail-grid">
          <div class="detail-item-full">
            <label>Profanity Filter:</label>
            <span class="full-text">{{ selectedConversation.profanity ? 'Enabled' : 'Disabled' }}</span>
          </div>
          <div class="detail-item-full">
            <label>Profanity Counter:</label>
            <span class="full-text">{{ selectedConversation.profanity_counter || 7 }}</span>
          </div>
          <div class="detail-item-full">
            <label>Funny Counter:</label>
            <span class="full-text">{{ selectedConversation.funny_counter || 4 }}</span>
          </div>
          <div class="detail-item-full">
            <label>Promo Counter:</label>
            <span class="full-text">{{ selectedConversation.promo_counter || 7 }}</span>
          </div>
          <div class="detail-item-full">
            <label>Group Title:</label>
            <span class="full-text">{{ selectedConversation.group_title || 'Not set' }}</span>
          </div>
          <div class="detail-item-full">
            <label>Question Asked:</label>
            <span class="full-text">{{ selectedConversation.question_asked || 'None' }}</span>
          </div>
        </div>
      </div>
      
      <!-- Intro/Outro Messages -->
      <div class="detail-group">
        <h3>Interview Messages</h3>
        <div class="detail-grid">
          <div class="detail-item-full">
            <label>Intro Message:</label>
            <span class="full-text">{{ selectedConversation.intro_msg || 'Not set' }}</span>
          </div>
          <div class="detail-item-full">
            <label>Outro Message:</label>
            <span class="full-text">{{ selectedConversation.outro_msg || 'Not set' }}</span>
          </div>
        </div>
      </div>
      
      <!-- Message Content from Memory -->
      <div class="detail-group">
        <h3>Conversation Messages - Memory ({{ conversationMessages.length }})</h3>
        <div v-if="conversationMessages.length === 0" class="empty">No messages</div>
        <div v-else class="messages-container">
          <div
            v-for="(msg, index) in conversationMessages"
            :key="index"
            class="message-item"
            :class="getRoleClass(msg.role)"
          >
            <div class="message-header">
              <span class="message-role">{{ getRoleLabel(msg.role) }}</span>
              <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
            </div>
            <div class="message-content">{{ msg.content }}</div>
          </div>
        </div>
      </div>

      <!-- SQL Conversation Table -->
      <div class="detail-group sql-messages">
        <h3>SQL Conversation Table ({{ sqlMessages.length }}{{ sqlTotal > sqlMessages.length ? ' of ' + sqlTotal : '' }})</h3>

        <div class="sql-controls">
          <div class="sql-search">
            <input v-model="sqlSearch" placeholder="Filter by user number..." @input="fetchSqlConversations" class="search-input" />
          </div>
          <div class="sql-pagination">
            <button @click="sqlOffset = 0; fetchSqlConversations()" :disabled="sqlOffset === 0" class="page-btn">First</button>
            <button @click="sqlOffset = Math.max(0, sqlOffset - sqlLimit); fetchSqlConversations()" :disabled="sqlOffset === 0" class="page-btn">Prev</button>
            <span class="page-info">{{ sqlOffset + 1 }}-{{ Math.min(sqlOffset + sqlLimit, sqlTotal) }} of {{ sqlTotal }}</span>
            <button @click="sqlOffset += sqlLimit; fetchSqlConversations()" :disabled="sqlOffset + sqlLimit >= sqlTotal" class="page-btn">Next</button>
            <button @click="sqlOffset = Math.floor((sqlTotal - 1) / sqlLimit) * sqlLimit; fetchSqlConversations()" :disabled="sqlOffset + sqlLimit >= sqlTotal" class="page-btn">Last</button>
          </div>
          <div class="sql-limit">
            <label>Limit:</label>
            <select v-model="sqlLimit" @change="fetchSqlConversations">
              <option :value="50">50</option>
              <option :value="100">100</option>
              <option :value="200">200</option>
              <option :value="500">500</option>
            </select>
          </div>
        </div>

        <div v-if="sqlLoading" class="loading">Loading SQL messages...</div>
        <div v-else-if="sqlMessages.length === 0" class="empty">No SQL messages found</div>
        <div v-else class="sql-messages-container">
          <div
            v-for="msg in sqlMessages"
            :key="msg.id"
            class="sql-message-item"
          >
            <div class="sql-message-header">
              <span class="sql-id">ID: {{ msg.id }}</span>
              <span class="sql-user">{{ msg.user_number }}</span>
              <span class="sql-time">{{ formatTime(msg.timestamp) }}</span>
            </div>
            <div class="sql-message-content">{{ msg.content }}</div>
          </div>
        </div>
      </div>
      
      <!-- Bot Questions -->
      <div v-if="botQuestions.length > 0" class="detail-group">
        <h3>Bot Questions ({{ botQuestions.length }})</h3>
        <div class="questions-container">
          <div 
            v-for="(q, index) in botQuestions" 
            :key="index"
            class="question-item"
          >
            <div class="question-header">
              <span class="question-id">Q{{ index + 1 }}</span>
              <span class="question-score" v-if="q.score">Score: {{ q.score }}</span>
            </div>
            <div class="question-text"><strong>Question:</strong> {{ q.question }}</div>
            <div class="answer-text" v-if="q.answer"><strong>Answer:</strong> {{ q.answer }}</div>
          </div>
        </div>
      </div>
      
      <!-- Action Buttons -->
      <div class="detail-actions">
        <button @click="testSend" class="action-btn primary">Test Send Message</button>
        <button @click="resetChannel" class="action-btn warning">Reset Channel</button>
        <button @click="callMethod" class="action-btn info">Call Background Task</button>
        <button @click="saveLogs" class="action-btn save">Save Logs</button>
      </div>
      
      <!-- Change Settings -->
      <div class="change-settings">
        <h3>Change Settings</h3>
        <div class="settings-grid">
          <div class="setting-item">
            <label>Set Persona:</label>
            <select v-model="newPersona" @change="updatePersona">
              <option value="">Choose persona...</option>
              <option v-for="p in personaOptions" :key="p.value" :value="p.value">{{ p.label }}</option>
            </select>
          </div>
          <div class="setting-item">
            <label>Set Mode:</label>
            <select v-model="newMode" @change="updateMode">
              <option value="">Choose mode...</option>
              <option v-for="m in convModeOptions" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
          </div>
          <div class="setting-item">
            <label>Set Type:</label>
            <select v-model="newConvType" @change="updateConvType">
              <option value="">Choose type...</option>
              <option v-for="t in convTypeOptions" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </div>
        </div>
      </div>
      
      <!-- Direct Message -->
      <div class="direct-message">
        <h3>Send Direct Message</h3>
        <textarea v-model="directMessage" placeholder="Type your message here..." rows="4" class="message-input"></textarea>
        <button @click="sendDirectMessage" class="action-btn success" :disabled="!directMessage.trim()">
          Send Message
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Message {
  role: string
  content: string
  timestamp?: number
}

interface BotQuestion {
  question: string
  answer: string
  score?: number
  metadata?: string
}

interface Conversation {
  user_number: string
  user_name: string
  bot_name?: string
  persona: string
  convmode: string
  convtype: string
  script?: string
  free_tries: number
  paid_messages: number
  message_count: number
  free_gpt?: boolean
  demo_user?: boolean
  interval?: number
  temperature?: number
  gpt_accessed?: number
  gpt_token_used?: number
  daily_free_gpt?: number
  profanity?: boolean
  profanity_counter?: number
  funny_counter?: number
  promo_counter?: number
  group_title?: string
  question_asked?: string
  intro_msg?: string
  outro_msg?: string
  messages?: Message[]
}

const stats = ref({
  active_conversations: 0,
  maintenance_mode: false,
  server_status: 'online',
  total_messages: 0,
  token_usage: 0
})

const conversations = ref<Conversation[]>([])
const filteredConversations = ref<Conversation[]>([])
const selectedConversation = ref<Conversation | null>(null)
const conversationMessages = ref<Message[]>([])
const botQuestions = ref<BotQuestion[]>([])
const loading = ref(false)
const sqlLoading = ref(false)
const sqlMessages = ref<any[]>([])
const sqlTotal = ref(0)
const sqlLimit = ref(100)
const sqlOffset = ref(0)
const sqlSearch = ref('')
const searchQuery = ref('')
const adminKey = ref('')
const newPersona = ref('')
const newMode = ref('')
const newConvType = ref('')
const directMessage = ref('')

// Persona options from conversations.py
const personaOptions = [
  { value: 'ASSISTANT', label: 'Assistant', description: 'General purpose AI assistant' },
  { value: 'USTAD', label: 'Ustad', description: 'Religious Advisor' },
  { value: 'HRD', label: 'HRD', description: 'Human Resources' },
  { value: 'CONTENT_MANAGER', label: 'Content Manager', description: 'Content strategy' },
  { value: 'CONTENT_CREATOR', label: 'Content Creator', description: 'Creative content' },
  { value: 'PSYCHOLOG', label: 'Psychologist', description: 'Psychologist' },
  { value: 'ROLEPLAY', label: 'Roleplay', description: 'Role play' },
  { value: 'VOLD', label: 'Vold', description: 'Vold character' },
  { value: 'INDOSOAI', label: 'IndoSoAI', description: 'Indonesian AI' },
  { value: 'KOBOLD', label: 'Kobold', description: 'Kobold AI' },
  { value: 'SALES_CS', label: 'Sales CS', description: 'Sales & Customer Service' },
  { value: 'KOS_CS', label: 'Kos CS', description: 'Kos rental service' },
  { value: 'FIT_TRAINER', label: 'Fit Trainer', description: 'Fitness Trainer' }
]

// ConvMode options from conversations.py
const convModeOptions = [
  { value: 'CHITCHAT', label: 'ChitChat', description: 'Casual chat mode' },
  { value: 'ASK', label: 'Ask', description: 'Question & Answer' },
  { value: 'THINK', label: 'Think', description: 'Deep thinking' },
  { value: 'QUIZ', label: 'Quiz', description: 'Quiz mode' },
  { value: 'TIMED', label: 'Timed', description: 'Timed responses' },
  { value: 'INTERVIEW', label: 'Interview', description: 'Interview mode' },
  { value: 'YESNO', label: 'YesNo', description: 'Yes/No questions' },
  { value: 'CHAIN', label: 'Chain', description: 'Chain conversation' }
]

// ConvType options from conversations.py
const convTypeOptions = [
  { value: 'DEMO', label: 'Demo', description: 'Demo user' },
  { value: 'FRIEND', label: 'Friend', description: 'Friend' },
  { value: 'GOLD', label: 'Gold', description: 'Gold user' },
  { value: 'PLATINUM', label: 'Platinum', description: 'Platinum user' },
  { value: 'ADMIN', label: 'Admin', description: 'Administrator' }
]

// Script options from conversations.py
const scriptOptions = [
  { value: 'BRAIN', label: 'Brain', description: 'Brain script' },
  { value: 'DEPARSE', label: 'Deparse', description: 'Deparse script' },
  { value: 'JS_OBJECTS', label: 'JS Objects', description: 'JavaScript objects' },
  { value: 'JSON_SERVER', label: 'JSON Server', description: 'JSON server' },
  { value: 'PARSER', label: 'Parser', description: 'Parser script' },
  { value: 'SESSIONS', label: 'Sessions', description: 'Sessions script' },
  { value: 'NEWCOMER', label: 'Newcomer', description: 'Newcomer script' },
  { value: 'INTERVIEW', label: 'Interview', description: 'Interview script' }
]

// Role options from conversations.py
const roleOptions = [
  { value: 'SYSTEM', label: 'System', description: 'System message' },
  { value: 'USER', label: 'User', description: 'User message' },
  { value: 'ASSISTANT', label: 'Assistant', description: 'Assistant message' }
]

const personas = personaOptions.map(p => p.value)
const modes = convModeOptions.map(m => m.value)
const convTypes = convTypeOptions.map(t => t.value)

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  adminKey.value = urlParams.get('admin_key') || ''
  refreshData()
  fetchSqlConversations()
})

const getPersonaLabel = (code: string): string => {
  const found = personaOptions.find(p => p.value === code)
  return found ? found.label : (code || 'Assistant')
}

const getConvModeLabel = (code: string): string => {
  const found = convModeOptions.find(m => m.value === code)
  return found ? found.label : (code || 'ChitChat')
}

const getConvTypeLabel = (code: string): string => {
  const found = convTypeOptions.find(t => t.value === code)
  return found ? found.label : (code || 'Demo')
}

const getScriptLabel = (code: string): string => {
  const found = scriptOptions.find(s => s.value === code)
  return found ? found.label : (code || 'Brain')
}

const getRoleLabel = (code: string): string => {
  const found = roleOptions.find(r => r.value === code)
  return found ? found.label : (code || 'User')
}

const getRoleClass = (role: string): string => {
  const normalizedRole = role.toUpperCase()
  if (normalizedRole === 'SYSTEM') return 'system'
  if (normalizedRole === 'USER') return 'user'
  return 'assistant'
}

const formatTime = (timestamp: number): string => {
  try {
    return new Date(timestamp).toLocaleString()
  } catch {
    return 'Unknown'
  }
}

const fetchSqlConversations = async () => {
  sqlLoading.value = true
  try {
    let url = `/api/admin/sql/conversations?limit=${sqlLimit.value}&offset=${sqlOffset.value}&admin_key=${encodeURIComponent(adminKey.value)}`
    if (sqlSearch.value.trim()) {
      url = `/api/admin/sql/conversations/${sqlSearch.value.trim()}?limit=${sqlLimit.value}&offset=${sqlOffset.value}&admin_key=${encodeURIComponent(adminKey.value)}`
    }
    const response = await fetch(url)
    if (response.ok) {
      const data = await response.json()
      sqlMessages.value = data.messages || []
      sqlTotal.value = data.total || data.messages?.length || 0
    }
  } catch (error) {
    console.error('Failed to fetch SQL conversations:', error)
  } finally {
    sqlLoading.value = false
  }
}

const fetchAPI = async (endpoint: string) => {
  const response = await fetch(`${endpoint}?admin_key=${encodeURIComponent(adminKey.value)}`)
  if (!response.ok) throw new Error('API call failed')
  return response.json()
}

const refreshData = async () => {
  loading.value = true
  try {
    const [statsRes, convsRes] = await Promise.all([
      fetchAPI('/api/admin/dashboard/stats'),
      fetchAPI('/api/admin/conversations')
    ])
    stats.value = statsRes
    conversations.value = convsRes
    filteredConversations.value = convsRes
  } catch (error) {
    console.error('Failed to fetch data:', error)
  } finally {
    loading.value = false
  }
}

const filterConversations = () => {
  if (!searchQuery.value.trim()) {
    filteredConversations.value = conversations.value
  } else {
    const query = searchQuery.value.toLowerCase()
    filteredConversations.value = conversations.value.filter(conv =>
      (conv.user_name || '').toLowerCase().includes(query) ||
      conv.user_number.toLowerCase().includes(query)
    )
  }
}

const selectConversation = async (conv: Conversation) => {
  selectedConversation.value = { ...conv }
  newPersona.value = ''
  newMode.value = ''
  newConvType.value = ''
  directMessage.value = ''
  conversationMessages.value = []
  botQuestions.value = []
  sqlSearch.value = conv.user_number
  fetchSqlConversations()

  // Fetch full conversation details
  try {
    const response = await fetch(`/obj_info/${conv.user_number}?admin_key=${encodeURIComponent(adminKey.value)}`)
    if (response.ok) {
      const data = await response.json()
      const result = data.message
      
      // Update with full details
      if (selectedConversation.value) {
        selectedConversation.value = {
          ...selectedConversation.value,
          bot_name: result.bot_name || 'Maya',
          script: result.script || 'BRAIN',
          free_gpt: result.free_gpt || false,
          demo_user: result.demo_user || true,
          gpt_accessed: result.gpt_accessed || 0,
          gpt_token_used: result.gpt_token_used || 0,
          daily_free_gpt: result.daily_free_gpt || 5,
          profanity: result.profanity || false,
          profanity_counter: result.profanity_counter || 7,
          funny_counter: result.funny_counter || 4,
          promo_counter: result.promo_counter || 7,
          group_title: result.group_title || '',
          question_asked: result.question_asked || '',
          intro_msg: result.intro_msg || '',
          outro_msg: result.outro_msg || ''
        }
      }
      
      // Parse messages
      if (result.messages) {
        try {
          conversationMessages.value = typeof result.messages === 'string' 
            ? JSON.parse(result.messages) 
            : result.messages
        } catch {
          conversationMessages.value = []
        }
      }
      
      // Parse bot questions
      if (result.botquestions && result.botquestions.length > 0) {
        botQuestions.value = result.botquestions
      }
    }
  } catch (error) {
    console.error('Failed to fetch conversation details:', error)
  }
}

const toggleMaintenance = async () => {
  try {
    await fetchAPI('/set_maintenance')
    await refreshData()
  } catch (error) {
    console.error('Failed to toggle maintenance:', error)
    alert('Failed to toggle maintenance mode')
  }
}

const pingServer = async () => {
  try {
    const response = await fetchAPI('/ping')
    alert('Server response: ' + response.message)
  } catch (error) {
    alert('Failed to ping server')
  }
}

const updatePersona = async () => {
  if (!selectedConversation.value || !newPersona.value) return
  try {
    await fetch(`/set_persona/${selectedConversation.value.user_number}/${newPersona.value}?admin_key=${encodeURIComponent(adminKey.value)}`)
    selectedConversation.value.persona = newPersona.value
    await refreshData()
    alert('Persona updated to: ' + getPersonaLabel(newPersona.value))
  } catch (error) {
    console.error('Failed to update persona:', error)
    alert('Failed to update persona')
  }
}

const updateMode = async () => {
  if (!selectedConversation.value || !newMode.value) return
  try {
    await fetch(`/set_convmode/${selectedConversation.value.user_number}/${newMode.value}?admin_key=${encodeURIComponent(adminKey.value)}`)
    selectedConversation.value.convmode = newMode.value
    await refreshData()
    alert('Mode updated to: ' + getConvModeLabel(newMode.value))
  } catch (error) {
    console.error('Failed to update mode:', error)
    alert('Failed to update mode')
  }
}

const updateConvType = async () => {
  if (!selectedConversation.value || !newConvType.value) return
  try {
    await fetch(`/set_convtype/${selectedConversation.value.user_number}/${newConvType.value}?admin_key=${encodeURIComponent(adminKey.value)}`)
    selectedConversation.value.convtype = newConvType.value
    await refreshData()
    alert('Type updated to: ' + getConvTypeLabel(newConvType.value))
  } catch (error) {
    console.error('Failed to update type:', error)
    alert('Failed to update type')
  }
}

const testSend = async () => {
  if (!selectedConversation.value) return
  try {
    const response = await fetch(`/test_send/${selectedConversation.value.user_number}?admin_key=${encodeURIComponent(adminKey.value)}`)
    const result = await response.json()
    alert('Test send result: ' + result.message)
  } catch (error) {
    console.error('Failed to test send:', error)
    alert('Failed to test send')
  }
}

const resetChannel = async () => {
  if (!selectedConversation.value) return
  if (!confirm('Are you sure you want to reset this channel?')) return
  try {
    const response = await fetch(`/reset_channel/${selectedConversation.value.user_number}?admin_key=${encodeURIComponent(adminKey.value)}`)
    const result = await response.json()
    alert('Reset result: ' + result.message)
    await refreshData()
  } catch (error) {
    console.error('Failed to reset channel:', error)
    alert('Failed to reset channel')
  }
}

const callMethod = async () => {
  if (!selectedConversation.value) return
  try {
    const response = await fetch(`/run_background_task/${selectedConversation.value.user_number}?admin_key=${encodeURIComponent(adminKey.value)}`)
    const result = await response.json()
    alert('Background task result: ' + result.message)
  } catch (error) {
    console.error('Failed to call method:', error)
    alert('Failed to call background task')
  }
}

const saveLogs = async () => {
  if (!selectedConversation.value) return
  try {
    const response = await fetchAPI('/save_logs')
    alert('Logs saved: ' + response.message)
  } catch (error) {
    console.error('Failed to save logs:', error)
    alert('Failed to save logs')
  }
}

const sendDirectMessage = async () => {
  if (!selectedConversation.value || !directMessage.value.trim()) return
  try {
    const response = await fetch('/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: directMessage.value,
        user_number: selectedConversation.value.user_number,
        bot_number: '6285775300227@c.us',
        type: 'chat'
      })
    })
    const result = await response.json()
    alert('Message sent: ' + (result.data || result.message || 'Success'))
    directMessage.value = ''
  } catch (error) {
    console.error('Failed to send message:', error)
    alert('Failed to send message')
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f0f2f5; }

.admin-dashboard { max-width: 1400px; margin: 0 auto; padding: 20px; }

.dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 16px; }
.dashboard-header h1 { font-size: 28px; color: #1f2937; }
.header-stats { display: flex; gap: 12px; flex-wrap: wrap; }

.stat-badge { padding: 10px 16px; background: white; border-radius: 8px; font-size: 14px; color: #374151; border: 1px solid #e5e7eb; font-weight: 500; }
.stat-badge.active { background: #dcfce7; color: #166534; border-color: #86efac; }

.control-panel { display: flex; gap: 12px; margin-bottom: 24px; flex-wrap: wrap; }

.control-btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 14px; transition: all 0.2s; }
.control-btn:hover { transform: translateY(-1px); }
.control-btn.primary { background: #3b82f6; color: white; }
.control-btn.success { background: #10b981; color: white; }
.control-btn.warning { background: #f59e0b; color: white; }
.control-btn.info { background: #8b5cf6; color: white; }
.control-btn.save { background: #06b6d4; color: white; }
.control-btn.active { background: #ef4444; color: white; }
.control-btn.refresh { background: #f3f4f6; color: #374151; border: 1px solid #d1d5db; }
.control-btn.ping { background: #ec4899; color: white; }

.conversations-section, .details-section { background: white; border-radius: 12px; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.conversations-section h2, .details-section h2 { font-size: 20px; color: #1f2937; margin-bottom: 16px; }

.search-box { margin-bottom: 16px; }
.search-input { width: 100%; padding: 12px 16px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 16px; }
.search-input:focus { outline: none; border-color: #3b82f6; box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }

.conversation-item { padding: 16px; border: 2px solid #e5e7eb; border-radius: 10px; margin-bottom: 12px; cursor: pointer; transition: all 0.2s; background: white; }
.conversation-item:hover { border-color: #3b82f6; background: #f8fafc; }
.conversation-item.active { border-color: #10b981; background: #f0fdf4; }

.conv-main { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; flex-wrap: wrap; gap: 12px; }
.conv-info { flex: 1; min-width: 200px; }
.conv-info strong { display: block; font-size: 16px; color: #1f2937; margin-bottom: 4px; }
.conv-number { font-size: 13px; color: #6b7280; font-family: monospace; }

.conv-badges { display: flex; gap: 8px; flex-wrap: wrap; }
.badge-full { padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; }
.badge-full.persona { background: #dbeafe; color: #1e40af; }
.badge-full.mode { background: #dcfce7; color: #166534; }
.badge-full.type { background: #fef3c7; color: #92400e; }

.conv-stats { display: flex; gap: 20px; font-size: 14px; color: #6b7280; }
.conv-stats span { font-weight: 500; }

.loading, .empty { text-align: center; padding: 40px; color: #6b7280; font-size: 16px; }

.details-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.details-header h2 { margin-bottom: 0 !important; }
.close-btn { padding: 8px 16px; background: #ef4444; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; }

.detail-group { margin-bottom: 24px; }
.detail-group h3 { font-size: 18px; color: #1f2937; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid #e5e7eb; }

.detail-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.detail-item-full { display: flex; flex-direction: column; gap: 4px; }
.detail-item-full label { font-weight: 600; color: #374151; font-size: 14px; }
.full-text { color: #1f2937; font-size: 16px; word-break: break-word; }

.badge-large { padding: 10px 16px; border-radius: 8px; font-size: 14px; font-weight: 600; display: inline-block; }
.badge-large.persona { background: #dbeafe; color: #1e40af; }
.badge-large.mode { background: #dcfce7; color: #166534; }
.badge-large.type { background: #fef3c7; color: #92400e; }

.messages-container { background: #f8fafc; border-radius: 8px; padding: 16px; max-height: 500px; overflow-y: auto; }
.message-item { padding: 12px; border-radius: 8px; margin-bottom: 12px; background: white; border: 1px solid #e5e7eb; }
.message-item:last-child { margin-bottom: 0; }
.message-item.system { border-left: 4px solid #8b5cf6; }
.message-item.user { border-left: 4px solid #3b82f6; }
.message-item.assistant { border-left: 4px solid #10b981; }

.message-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.message-role { font-weight: 600; color: #374151; font-size: 16px; }
.message-time { font-size: 14px; color: #9ca3af; }
.message-content { font-size: 18px; color: #1f2937; line-height: 1.7; white-space: pre-wrap; word-break: break-word; }

.questions-container { background: #f8fafc; border-radius: 8px; padding: 16px; }
.question-item { padding: 12px; border-radius: 8px; margin-bottom: 12px; background: white; border: 1px solid #e5e7eb; }
.question-item:last-child { margin-bottom: 0; }
.question-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.question-id { font-weight: 600; color: #3b82f6; }
.question-score { font-size: 12px; color: #10b981; }
.question-text, .answer-text { font-size: 14px; color: #1f2937; margin-bottom: 4px; }
.question-text strong, .answer-text strong { color: #374151; }

.sql-messages { background: #fffbeb; border: 1px solid #fcd34d; border-radius: 8px; padding: 16px; }
.sql-messages h3 { color: #92400e; border-bottom-color: #fcd34d; }
.sql-controls { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; align-items: center; }
.sql-search { flex: 1; min-width: 200px; }
.sql-search input { width: 100%; padding: 10px 14px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; }
.sql-pagination { display: flex; gap: 8px; align-items: center; }
.page-btn { padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 6px; background: white; cursor: pointer; font-size: 13px; }
.page-btn:hover:not(:disabled) { background: #f3f4f6; }
.page-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.page-info { font-size: 13px; color: #6b7280; }
.sql-limit { display: flex; gap: 8px; align-items: center; }
.sql-limit label { font-size: 13px; color: #6b7280; }
.sql-limit select { padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 13px; }
.sql-messages-container { background: white; border-radius: 8px; padding: 16px; max-height: 600px; overflow-y: auto; }
.sql-message-item { padding: 16px; border-radius: 6px; margin-bottom: 10px; background: #fefce8; border: 1px solid #fef08a; }
.sql-message-item:last-child { margin-bottom: 0; }
.sql-message-header { display: flex; gap: 12px; align-items: center; margin-bottom: 10px; flex-wrap: wrap; }
.sql-id { font-weight: 600; color: #92400e; font-size: 15px; }
.sql-user { font-family: monospace; font-size: 16px; color: #059669; }
.sql-time { font-size: 14px; color: #9ca3af; }
.sql-message-content { font-size: 18px; color: #1f2937; line-height: 1.7; white-space: pre-wrap; word-break: break-word; }

.detail-actions { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 24px; }
.action-btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 14px; transition: all 0.2s; }
.action-btn:hover { transform: translateY(-1px); }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.action-btn.primary { background: #3b82f6; color: white; }
.action-btn.success { background: #10b981; color: white; }
.action-btn.warning { background: #f59e0b; color: white; }
.action-btn.info { background: #8b5cf6; color: white; }
.action-btn.save { background: #06b6d4; color: white; }

.change-settings, .direct-message { border-top: 1px solid #e5e7eb; padding-top: 20px; margin-top: 20px; }
.change-settings h3, .direct-message h3 { font-size: 18px; color: #1f2937; margin-bottom: 16px; }

.settings-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; }
.setting-item { display: flex; flex-direction: column; gap: 8px; }
.setting-item label { font-weight: 600; color: #374151; }
.setting-item select { padding: 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background: white; }
.setting-item select:focus { outline: none; border-color: #3b82f6; }

.message-input { width: 100%; padding: 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; font-family: inherit; margin-bottom: 12px; resize: vertical; }
.message-input:focus { outline: none; border-color: #3b82f6; }

@media (max-width: 768px) {
  .dashboard-header { flex-direction: column; align-items: flex-start; }
  .control-panel { flex-direction: column; }
  .detail-grid { grid-template-columns: 1fr; }
  .settings-grid { grid-template-columns: 1fr; }
  .conv-main { flex-direction: column; }
  .detail-actions { flex-direction: column; }
}
</style>