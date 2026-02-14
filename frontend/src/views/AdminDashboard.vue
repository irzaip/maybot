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
      
      <!-- Two Column Layout -->
      <div class="two-column-layout">
        <!-- Left Column: Conversation List -->
        <div class="conversation-list-panel">
          <div v-if="loading" class="loading">Loading...</div>
          <div v-else-if="filteredConversations.length === 0" class="empty">No conversations found</div>
          <div v-else class="conversation-list compact">
            <div 
              v-for="conv in filteredConversations" 
              :key="conv.user_number"
              class="conversation-item compact"
              :class="{ active: selectedConversation?.user_number === conv.user_number }"
              @click="selectConversation(conv)"
            >
              <span class="conv-name">{{ conv.user_name || 'Unknown' }}</span>
              <span class="conv-number">{{ conv.user_number }}</span>
              <span class="badge-sm persona">{{ getPersonaLabel(conv.persona) }}</span>
              <span class="badge-sm mode">{{ getConvModeLabel(conv.convmode) }}</span>
              <span class="badge-sm type">{{ getConvTypeLabel(conv.convtype) }}</span>
            </div>
          </div>
        </div>
        
        <!-- Right Column: Conversation Details -->
        <div class="details-panel">
          <div v-if="!selectedConversation" class="no-selection">
            <p>Select a conversation to view details</p>
          </div>
          <div v-else class="details-section">
            <div class="details-header">
              <h3>{{ selectedConversation.user_name || 'Unknown' }}</h3>
              <button @click="selectedConversation = null" class="close-btn-sm">×</button>
            </div>
            
            <div class="detail-group">
              <div class="detail-grid">
                <div class="detail-item-full">
                  <label>Number:</label>
                  <span class="full-text">{{ selectedConversation.user_number }}</span>
                </div>
                <div class="detail-item-full">
                  <label>Bot Name:</label>
                  <span>{{ selectedConversation.bot_name || 'Maya' }}</span>
                </div>
                <div class="detail-item-full">
                  <label>Persona:</label>
                  <span class="badge-large persona">{{ getPersonaLabel(selectedConversation.persona) }}</span>
                </div>
                <div class="detail-item-full">
                  <label>Mode:</label>
                  <span class="badge-large mode">{{ getConvModeLabel(selectedConversation.convmode) }}</span>
                </div>
                <div class="detail-item-full">
                  <label>Type:</label>
                  <span class="badge-large type">{{ getConvTypeLabel(selectedConversation.convtype) }}</span>
                </div>
                <div class="detail-item-full">
                  <label>Interval:</label>
                  <span>{{ selectedConversation.interval || 600 }}s</span>
                </div>
                <div class="detail-item-full">
                  <label>Temp:</label>
                  <span>{{ selectedConversation.temperature || 0.7 }}</span>
                </div>
              </div>
            </div>
            
            <!-- Action Buttons -->
            <div class="detail-actions">
              <button @click="testSend" class="action-btn primary">Test Send</button>
              <button @click="resetChannel" class="action-btn warning">Reset</button>
              <button @click="callMethod" class="action-btn info">Run Task</button>
            </div>
            
            <!-- Change Settings -->
            <div class="change-settings">
              <h4>Change Settings</h4>
              <div class="settings-grid">
                <div class="setting-item">
                  <label>Persona:</label>
                  <select v-model="newPersona">
                    <option v-for="p in personas" :key="p" :value="p">{{ p }}</option>
                  </select>
                </div>
                <div class="setting-item">
                  <label>Mode:</label>
                  <select v-model="newMode">
                    <option v-for="m in modes" :key="m" :value="m">{{ m }}</option>
                  </select>
                </div>
                <div class="setting-item">
                  <label>Type:</label>
                  <select v-model="newConvType">
                    <option v-for="t in convTypes" :key="t" :value="t">{{ t }}</option>
                  </select>
                </div>
              </div>
              <div style="margin-top:12px; display: flex; gap: 8px;">
                <button @click="updatePersona" class="action-btn success">Update Persona</button>
                <button @click="updateMode" class="action-btn info">Update Mode</button>
                <button @click="updateConvType" class="action-btn warning">Update Type</button>
              </div>
            </div>
            
            <!-- Direct Message -->
            <div class="direct-message">
              <h4>Send Message</h4>
              <textarea v-model="directMessage" placeholder="Type message..." class="message-input" rows="3"></textarea>
              <button @click="sendDirectMessage" class="action-btn primary">Send</button>
            </div>
            
            <!-- SQL Messages Section -->
            <div class="sql-messages">
              <h3>SQL Messages</h3>
              <div class="sql-controls">
                <div class="sql-search">
                  <input v-model="sqlSearch" placeholder="Search..." @input="fetchSqlConversations" />
                </div>
                <button @click="fetchSqlConversations" class="control-btn refresh" style="padding:8px 12px">Refresh</button>
              </div>
              <div v-if="sqlLoading" class="loading">Loading SQL messages...</div>
              <div v-else class="sql-messages-container">
                <div v-for="msg in sqlMessages" :key="msg.id" class="sql-message-item" :class="msg.direction">
                  <div class="sql-message-header">
                    <span class="sql-id">#{{ msg.id }}</span>
                    <span class="sql-dir" :class="msg.direction">{{ msg.direction === 'incoming' ? '⬇️ IN' : '⬆️ OUT' }}</span>
                    <span class="sql-user">{{ msg.user_number }}</span>
                    <span class="sql-time">{{ formatTime(msg.timestamp) }}</span>
                  </div>
                  <div class="sql-message-content">{{ msg.content }}</div>
                </div>
                <div v-if="sqlMessages.length === 0" class="empty">No messages found</div>
              </div>
            </div>
          </div>
        </div>
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
  demo_user?: boolean
  interval?: number
  temperature?: number
  profanity?: boolean
  profanity_counter?: number
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
  sqlMessages.value = []
  try {
    let url = `/api/admin/sql/conversations?limit=${sqlLimit.value}&offset=${sqlOffset.value}&admin_key=${encodeURIComponent(adminKey.value)}`
    if (sqlSearch.value.trim()) {
      url = `/api/admin/sql/conversations/${encodeURIComponent(sqlSearch.value.trim())}?limit=${sqlLimit.value}&offset=${sqlOffset.value}&admin_key=${encodeURIComponent(adminKey.value)}`
    }
    console.log('Fetching SQL:', url)
    const response = await fetch(url)
    console.log('Response status:', response.status)
    if (response.ok) {
      const data = await response.json()
      console.log('SQL data:', data)
      sqlMessages.value = data.messages || []
      sqlTotal.value = data.total || data.messages?.length || 0
    } else {
      console.error('SQL fetch error:', response.status, await response.text())
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
          demo_user: result.demo_user || true,
          profanity: result.profanity || false,
          profanity_counter: result.profanity_counter || 7,
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
    const response = await fetch(`/set_persona/${selectedConversation.value.user_number}/${newPersona.value}`, {
      method: 'PUT'
    })
    const result = await response.json()
    console.log('Update persona result:', result)
    selectedConversation.value.persona = newPersona.value
    await refreshData()
    alert('Persona updated to: ' + newPersona.value)
  } catch (error) {
    console.error('Failed to update persona:', error)
    alert('Failed to update persona')
  }
}

const updateMode = async () => {
  if (!selectedConversation.value || !newMode.value) return
  try {
    const response = await fetch(`/set_convmode/${selectedConversation.value.user_number}/${newMode.value}`, {
      method: 'PUT'
    })
    const result = await response.json()
    console.log('Update mode result:', result)
    selectedConversation.value.convmode = newMode.value
    alert('Mode updated to: ' + newMode.value)
  } catch (error) {
    console.error('Failed to update mode:', error)
    alert('Failed to update mode')
  }
}

const updateConvType = async () => {
  if (!selectedConversation.value || !newConvType.value) return
  try {
    const response = await fetch(`/set_convtype/${selectedConversation.value.user_number}/${newConvType.value}`, {
      method: 'PUT'
    })
    const result = await response.json()
    console.log('Update type result:', result)
    selectedConversation.value.convtype = newConvType.value
    alert('Type updated to: ' + newConvType.value)
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
.sql-message-item.incoming { background: #e0f2fe; border-color: #7dd3fc; }
.sql-message-item.outgoing { background: #dcfce7; border-color: #86efac; }
.sql-message-item:last-child { margin-bottom: 0; }
.sql-dir { font-weight: bold; font-size: 12px; padding: 2px 6px; border-radius: 4px; }
.sql-dir.incoming { background: #0ea5e9; color: white; }
.sql-dir.outgoing { background: #22c55e; color: white; }
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

/* Two Column Layout */
.two-column-layout {
  display: grid;
  grid-template-columns: minmax(300px, 1fr) minmax(350px, 1fr);
  gap: 20px;
  width: 100%;
}
.conversation-list-panel { 
  max-height: 70vh; 
  overflow-y: auto; 
  padding-right: 10px;
}
.details-panel { 
  max-height: 70vh; 
  overflow-y: auto; 
}

.conversation-list.compact { display: flex; flex-direction: column; gap: 6px; }
.conversation-item.compact { 
  padding: 10px 12px; 
  border: 1px solid #e5e7eb; 
  border-radius: 8px; 
  display: flex; 
  align-items: center; 
  gap: 8px; 
  flex-wrap: wrap;
  font-size: 12px;
}
.conversation-item.compact:hover { border-color: #3b82f6; background: #f8fafc; }
.conversation-item.compact.active { border-color: #10b981; background: #f0fdf4; }

.conv-name { font-weight: 600; color: #1f2937; min-width: 80px; }
.conv-number { font-size: 11px; color: #9ca3af; font-family: monospace; }
.badge-sm { padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; }
.badge-sm.persona { background: #dbeafe; color: #1e40af; }
.badge-sm.mode { background: #dcfce7; color: #166534; }
.badge-sm.type { background: #fef3c7; color: #92400e; }

.no-selection { 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  height: 200px; 
  background: #f9fafb; 
  border: 2px dashed #e5e7eb; 
  border-radius: 12px;
  color: #9ca3af;
}

.details-section { background: white; border-radius: 12px; padding: 20px; border: 1px solid #e5e7eb; }
.details-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.details-header h3 { margin: 0; font-size: 18px; color: #1f2937; }
.close-btn-sm { background: #ef4444; color: white; border: none; border-radius: 4px; width: 28px; height: 28px; cursor: pointer; font-size: 18px; line-height: 1; }

@media (max-width: 1024px) {
  .two-column-layout { grid-template-columns: 1fr; }
  .conversation-list-panel { max-height: 400px; }
  .details-panel { max-height: 400px; }
}

@media (max-width: 768px) {
  .dashboard-header { flex-direction: column; align-items: flex-start; }
  .control-panel { flex-direction: column; }
  .detail-grid { grid-template-columns: 1fr; }
  .settings-grid { grid-template-columns: 1fr; }
  .conv-main { flex-direction: column; }
  .detail-actions { flex-direction: column; }
}
</style>