<template>
  <div class="conversation-manager">
    <div class="manager-header">
      <h3>Conversations</h3>
      <div class="header-actions">
        <div class="search-container">
          <input 
            v-model="searchQuery" 
            placeholder="Search conversations..."
            @input="handleSearch"
            class="search-input"
          />
          <div class="search-icon">🔍</div>
        </div>
        
        <button 
          @click="refreshConversations"
          :disabled="loading"
          class="refresh-btn"
          title="Refresh conversations"
        >
          🔄
        </button>
      </div>
    </div>
    
    <!-- Bulk Operations Bar -->
    <div v-if="selectedIds.length > 0" class="bulk-operations">
      <div class="bulk-info">
        {{ selectedIds.length }} conversation{{ selectedIds.length > 1 ? 's' : '' }} selected
      </div>
      
      <div class="bulk-controls">
        <select v-model="bulkPersona" class="bulk-select">
          <option value="">Set Persona...</option>
          <option v-for="persona in personas" :key="persona" :value="persona">
            {{ persona }}
          </option>
        </select>
        
        <select v-model="bulkConvMode" class="bulk-select">
          <option value="">Set Mode...</option>
          <option v-for="mode in convModes" :key="mode" :value="mode">
            {{ mode }}
          </option>
        </select>
        
        <button 
          @click="applyBulkOperations"
          :disabled="!hasBulkChanges"
          class="bulk-apply-btn"
        >
          Apply Changes
        </button>
        
        <button 
          @click="clearSelection"
          class="bulk-clear-btn"
        >
          Clear Selection
        </button>
      </div>
    </div>
    
    <!-- Conversation List -->
    <div class="conversations-container">
      <div 
        v-for="conv in filteredConversations" 
        :key="conv.user_number"
        class="conversation-item"
        :class="{ 
          selected: selectedIds.includes(conv.user_number),
          active: selectedConversation?.user_number === conv.user_number
        }"
      >
        <div class="conversation-select">
          <input 
            type="checkbox" 
            :checked="selectedIds.includes(conv.user_number)"
            @change="toggleSelection(conv.user_number)"
            class="conversation-checkbox"
          />
        </div>
        
        <div 
          class="conversation-content"
          @click="$emit('select-conversation', conv)"
        >
          <div class="conversation-header">
            <div class="user-info">
              <span class="user-name">{{ conv.user_name || 'Unknown' }}</span>
              <span class="user-number">{{ conv.user_number }}</span>
            </div>
            
            <div class="conversation-stats">
              <span class="message-count">{{ conv.message_count }} msgs</span>
              <span v-if="conv.last_active" class="last-active">
                {{ formatLastActive(conv.last_active) }}
              </span>
            </div>
          </div>
          
          <div class="conversation-badges">
            <span :class="['badge', 'persona', conv.persona.toLowerCase()]">
              {{ conv.persona }}
            </span>
            <span :class="['badge', 'mode', conv.convmode.toLowerCase()]">
              {{ conv.convmode }}
            </span>
            <span :class="['badge', 'type', conv.convtype.toLowerCase()]">
              {{ conv.convtype }}
            </span>
          </div>
          
        </div>
        
        <div class="conversation-actions">
          <button 
            @click.stop="resetChannel(conv.user_number)"
            class="action-btn reset"
            title="Reset conversation"
          >
            🔄
          </button>
          <button 
            @click.stop="testSend(conv.user_number)"
            class="action-btn test"
            title="Send test message"
          >
            📤
          </button>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="loading && conversations.length === 0" class="loading-state">
        <div class="loading-spinner"></div>
        <span>Loading conversations...</span>
      </div>
      
      <!-- Empty State -->
      <div v-if="!loading && filteredConversations.length === 0" class="empty-state">
        <div class="empty-icon">📱</div>
        <h4>No conversations found</h4>
        <p>{{ searchQuery ? 'Try adjusting your search terms' : 'No active conversations' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { adminApi } from '@/api/client'
import { Persona, ConvMode, ConvType } from '@/types'
import type { ConversationListItem, Conversation } from '@/types'

const props = defineProps<{
  conversations: ConversationListItem[]
  selectedConversation: Conversation | null
  loading: boolean
}>()

const emit = defineEmits([
  'select-conversation', 
  'bulk-operation', 
  'search-conversations'
])

const searchQuery = ref('')
const selectedIds = ref<string[]>([])
const bulkPersona = ref('')
const bulkConvMode = ref('')

const personas = Object.values(Persona)
const convModes = Object.values(ConvMode)

const filteredConversations = computed(() => {
  let filtered = props.conversations
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(conv => 
      conv.user_name.toLowerCase().includes(query) ||
      conv.user_number.toLowerCase().includes(query) ||
      conv.persona.toLowerCase().includes(query) ||
      conv.convmode.toLowerCase().includes(query) ||
      conv.convtype.toLowerCase().includes(query)
    )
  }
  
  return filtered.sort((a, b) => b.message_count - a.message_count)
})

const hasBulkChanges = computed(() => {
  return bulkPersona.value || bulkConvMode.value
})

const handleSearch = () => {
  emit('search-conversations', searchQuery.value)
}

const toggleSelection = (userNumber: string) => {
  const index = selectedIds.value.indexOf(userNumber)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(userNumber)
  }
}

const clearSelection = () => {
  selectedIds.value = []
  bulkPersona.value = ''
  bulkConvMode.value = ''
}

const applyBulkOperations = async () => {
  if (selectedIds.value.length === 0 || !hasBulkChanges.value) return
  
  try {
    const operations = []
    
    if (bulkPersona.value) {
      await adminApi.bulkSetPersona(selectedIds.value, bulkPersona.value as Persona)
      operations.push(`Persona: ${bulkPersona.value}`)
    }
    
    if (bulkConvMode.value) {
      await adminApi.bulkSetConvMode(selectedIds.value, bulkConvMode.value as ConvMode)
      operations.push(`Mode: ${bulkConvMode.value}`)
    }
    
    emit('bulk-operation', {
      userNumbers: selectedIds.value,
      operations,
      success: true
    })
    
    clearSelection()
    
  } catch (error) {
    console.error('Bulk operation failed:', error)
    emit('bulk-operation', {
      userNumbers: selectedIds.value,
      success: false,
      error
    })
  }
}

const resetChannel = async (userNumber: string) => {
  try {
    await adminApi.resetChannel(userNumber)
    // Show success feedback
    console.log(`Reset channel for ${userNumber}`)
  } catch (error) {
    console.error('Failed to reset channel:', error)
  }
}

const testSend = async (userNumber: string) => {
  try {
    const response = await adminApi.testSend(userNumber)
    console.log(`Test send to ${userNumber}:`, response.data)
  } catch (error) {
    console.error('Test send failed:', error)
  }
}

const refreshConversations = () => {
  emit('search-conversations', searchQuery.value)
}

const formatLastActive = (lastActive: string): string => {
  try {
    const date = new Date(lastActive)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    return `${diffDays}d ago`
  } catch {
    return 'Unknown'
  }
}

// Clear selection when conversations change
watch(() => props.conversations, () => {
  clearSelection()
})
</script>

<style scoped>
.conversation-manager {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.manager-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-container {
  position: relative;
}

.search-input {
  padding: 8px 12px 8px 36px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  width: 250px;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
}

.refresh-btn {
  padding: 8px 12px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.refresh-btn:hover:not(:disabled) {
  background: #e5e7eb;
}

.bulk-operations {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bulk-info {
  font-weight: 600;
  color: #374151;
}

.bulk-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.bulk-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  min-width: 120px;
}

.bulk-apply-btn {
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.bulk-apply-btn:hover:not(:disabled) {
  background: #2563eb;
}

.bulk-apply-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.bulk-clear-btn {
  padding: 8px 16px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.bulk-clear-btn:hover {
  background: #e5e7eb;
}

.conversations-container {
  max-height: 600px;
  overflow-y: auto;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.2s ease;
}

.conversation-item:hover {
  border-color: #d1d5db;
  background: #f8fafc;
}

.conversation-item.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.conversation-item.active {
  border-color: #10b981;
  background: #ecfdf5;
}

.conversation-checkbox {
  width: 16px;
  height: 16px;
}

.conversation-content {
  flex: 1;
  cursor: pointer;
}

.conversation-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.user-number {
  font-size: 12px;
  color: #6b7280;
}

.conversation-stats {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.message-count {
  font-weight: 600;
  color: #374151;
  font-size: 12px;
}

.last-active {
  font-size: 11px;
  color: #9ca3af;
}

.conversation-badges {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge.persona { background: #dbeafe; color: #1e40af; }
.badge.mode { background: #dcfce7; color: #166534; }
.badge.type { background: #fef3c7; color: #92400e; }

.usage-info {
  display: flex;
  gap: 16px;
}

.usage-item {
  display: flex;
  gap: 4px;
  font-size: 12px;
}

.usage-label {
  color: #6b7280;
}

.usage-value {
  font-weight: 600;
  color: #1f2937;
}

.conversation-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 16px;
}

.action-btn:hover {
  border-color: #9ca3af;
  background: #f8fafc;
}

.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #6b7280;
  text-align: center;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h4 {
  margin: 0 0 8px 0;
  color: #374151;
}

.empty-state p {
  margin: 0;
  color: #6b7280;
}

@media (max-width: 768px) {
  .manager-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .search-input {
    width: 200px;
  }
  
  .bulk-operations {
    flex-direction: column;
    gap: 12px;
  }
  
  .bulk-controls {
    flex-wrap: wrap;
  }
  
  .conversation-header {
    flex-direction: column;
    gap: 8px;
  }
  
  .usage-info {
    margin-top: 8px;
  }
}
</style>