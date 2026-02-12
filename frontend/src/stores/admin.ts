import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DashboardStats, ConversationListItem, Conversation } from '@/types'
import { adminApi } from '@/api/client'

export const useAdminStore = defineStore('admin', () => {
  // State
  const dashboardStats = ref<DashboardStats>({
    active_conversations: 0,
    maintenance_mode: false,
    server_status: 'offline',
    total_messages: 0,
    token_usage: 0
  })

  const conversations = ref<ConversationListItem[]>([])
  const selectedConversation = ref<Conversation | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const activeConversationsCount = computed(() => 
    conversations.value.filter(c => c.message_count > 0).length
  )

  const conversationsByPersona = computed(() => {
    const grouped: Record<string, ConversationListItem[]> = {}
    conversations.value.forEach(conv => {
      if (!grouped[conv.persona]) {
        grouped[conv.persona] = []
      }
      grouped[conv.persona].push(conv)
    })
    return grouped
  })

  // Actions
  async function loadDashboardStats() {
    try {
      loading.value = true
      const response = await adminApi.getDashboardStats()
      dashboardStats.value = response.data
      error.value = null
    } catch (err: any) {
      error.value = `Failed to load dashboard stats: ${err.message}`
      console.error('Error loading dashboard stats:', err)
    } finally {
      loading.value = false
    }
  }

  async function loadConversations(search?: string) {
    try {
      loading.value = true
      const response = await adminApi.getConversations(search)
      conversations.value = response.data
      error.value = null
    } catch (err: any) {
      error.value = `Failed to load conversations: ${err.message}`
      console.error('Error loading conversations:', err)
    } finally {
      loading.value = false
    }
  }

  async function loadConversationDetails(userNumber: string) {
    try {
      loading.value = true
      const response = await adminApi.getConversationInfo(userNumber)
      selectedConversation.value = response.data
      error.value = null
    } catch (err: any) {
      error.value = `Failed to load conversation details: ${err.message}`
      console.error('Error loading conversation details:', err)
    } finally {
      loading.value = false
    }
  }

  async function refreshData() {
    await Promise.all([
      loadDashboardStats(),
      loadConversations()
    ])
  }

  function selectConversation(conversation: ConversationListItem) {
    loadConversationDetails(conversation.user_number)
  }

  function clearError() {
    error.value = null
  }

  function updateConversationInList(updatedConversation: ConversationListItem) {
    const index = conversations.value.findIndex(c => c.user_number === updatedConversation.user_number)
    if (index > -1) {
      conversations.value[index] = updatedConversation
    }
  }

  return {
    // State
    dashboardStats,
    conversations,
    selectedConversation,
    loading,
    error,
    
    // Getters
    activeConversationsCount,
    conversationsByPersona,
    
    // Actions
    loadDashboardStats,
    loadConversations,
    loadConversationDetails,
    refreshData,
    selectConversation,
    clearError,
    updateConversationInList
  }
})