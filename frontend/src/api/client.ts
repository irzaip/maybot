import axios from 'axios'
import type { 
  DashboardStats, 
  Conversation, 
  ConversationListItem, 
  BulkOperationRequest,
  MessageContent,
  Role,
  Persona,
  ConvMode,
  ConvType
} from '@/types'

const API_BASE = '/api'
const ADMIN_KEY = new URLSearchParams(window.location.search).get('admin_key') || ''

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  params: { admin_key: ADMIN_KEY }
})

export const adminApi = {
  // Dashboard
  getDashboardStats(): Promise<{ data: DashboardStats }> {
    return apiClient.get('/admin/dashboard/stats')
  },

  // Conversations
  getConversations(search?: string, limit = 100): Promise<{ data: ConversationListItem[] }> {
    return apiClient.get('/admin/conversations', { 
      params: { search, limit } 
    })
  },

  getConversationInfo(userNumber: string): Promise<{ data: Conversation }> {
    return apiClient.get(`/obj_info/${userNumber}`)
  },

  getConversationMessages(userNumber: string): Promise<{ data: any }> {
    return apiClient.get(`/print_messages/${userNumber}`)
  },

  createConversation(userNumber: string, botNumber: string): Promise<{ data: { message: string } }> {
    return apiClient.put(`/create_conv/${userNumber}/${botNumber}`)
  },

  // Basic operations
  setPersona(userNumber: string, persona: Persona): Promise<{ data: { message: string } }> {
    return apiClient.put(`/set_persona/${userNumber}/${persona}`)
  },

  setConvMode(userNumber: string, convmode: ConvMode): Promise<{ data: { message: string } }> {
    return apiClient.put(`/set_convmode/${userNumber}/${convmode}`)
  },

  setConvType(userNumber: string, convtype: ConvType): Promise<{ data: { message: string } }> {
    return apiClient.put(`/set_convtype/${userNumber}/${convtype}`)
  },

  setInterval(userNumber: string, interval: number): Promise<{ data: { message: string } }> {
    return apiClient.put(`/set_interval/${userNumber}/${interval}`)
  },

  setBotName(userNumber: string, botName: string): Promise<{ data: { message: string } }> {
    return apiClient.put(`/set_bot_name/${userNumber}/${botName}`)
  },

  // Message operations
  setMessage(userNumber: string, message: string, role: Role): Promise<{ data: { message: string } }> {
    return apiClient.post('/set_content', {
      user_number: userNumber,
      bot_number: "6285775300227@c.us",
      message,
      role
    })
  },

  setSystemMessage(userNumber: string, message: string): Promise<{ data: { message: string } }> {
    return apiClient.post('/set_content', {
      user_number: userNumber,
      bot_number: "6285775300227@c.us",
      message,
      role: 'SYSTEM'
    })
  },

  setUserMessage(userNumber: string, message: string): Promise<{ data: { message: string } }> {
    return apiClient.post('/set_content', {
      user_number: userNumber,
      bot_number: "6285775300227@c.us",
      message,
      role: 'USER'
    })
  },

  setAssistantMessage(userNumber: string, message: string): Promise<{ data: { message: string } }> {
    return apiClient.post('/set_content', {
      user_number: userNumber,
      bot_number: "6285775300227@c.us",
      message,
      role: 'ASSISTANT'
    })
  },

  // Usage limits

  resetChannel(userNumber: string): Promise<{ data: { message: string } }> {
    return apiClient.get(`/reset_channel/${userNumber}`)
  },

  // Interview and questions
  setInterviewMessages(userNumber: string, introMsg: string, outroMsg: string): Promise<{ data: { message: string } }> {
    return apiClient.put(`/set_interview/${userNumber}`, {
      intro_msg: introMsg,
      outro_msg: outroMsg
    })
  },

  startQuestioning(userNumber: string): Promise<{ data: { message: string } }> {
    return apiClient.get(`/start_question/${userNumber}`)
  },

  resetBotQuestions(userNumber: string): Promise<{ data: { message: string } }> {
    return apiClient.get(`/reset_botquestions/${userNumber}`)
  },

  getBotQuestions(userNumber: string): Promise<{ data: { message: string } }> {
    return apiClient.get(`/botquestions/${userNumber}`)
  },

  // System operations
  toggleMaintenance(): Promise<{ data: { message: string } }> {
    return apiClient.get('/set_maintenance')
  },

  saveLogs(): Promise<{ data: { message: string } }> {
    return apiClient.get('/save_logs')
  },

  rebuildConnectionDb(): Promise<{ data: { message: string } }> {
    return apiClient.get('/rebuild_connection_db')
  },

  callBackgroundTask(): Promise<{ data: { message: string } }> {
    return apiClient.get('/call_method')
  },

  // Testing and messaging
  testSend(userNumber: string): Promise<{ data: { message: string } }> {
    return apiClient.get(`/test_send/${userNumber}`)
  },

  sendMessage(userNumber: string, message: string): Promise<any> {
    return apiClient.post('/messages', {
      text: message,
      user_number: userNumber,
      bot_number: "6285775300227@c.us",
      type: 'chat'
    })
  },

  ping(): Promise<{ data: { message: string } }> {
    return apiClient.get('/ping')
  },

  listConversations(): Promise<{ data: { message: string[] } }> {
    return apiClient.get('/list_conversations')
  },

  // Bulk operations
  bulkSetPersona(userNumbers: string[], persona: Persona): Promise<{ data: { message: string } }> {
    return apiClient.post('/admin/bulk/persona', {
      user_numbers: userNumbers,
      persona
    })
  },

  bulkSetConvMode(userNumbers: string[], convmode: ConvMode): Promise<{ data: { message: string } }> {
    return apiClient.post('/admin/bulk/convmode', {
      user_numbers: userNumbers,
      convmode
    })
  },

  bulkSetConvType(userNumbers: string[], convtype: ConvType): Promise<{ data: { message: string } }> {
    return apiClient.post('/admin/bulk/convtype', {
      user_numbers: userNumbers,
      convtype
    })
  }
}

// WebSocket connection for real-time updates
export class WebSocketManager {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000

  connect(onMessage: (data: any) => void) {
    try {
      const adminKey = new URLSearchParams(window.location.search).get('admin_key')
      const wsUrl = `ws://${window.location.host}/api/admin/ws?admin_key=${adminKey}`
      
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.attemptReconnect(onMessage)
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      this.attemptReconnect(onMessage)
    }
  }

  private attemptReconnect(onMessage: (data: any) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      
      setTimeout(() => {
        this.connect(onMessage)
      }, this.reconnectDelay)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }
}

export const wsManager = new WebSocketManager()