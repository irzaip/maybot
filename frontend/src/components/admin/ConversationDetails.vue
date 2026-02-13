<template>
  <div class="conversation-details">
    <div class="details-header">
      <h3>Conversation Details</h3>
      <button @click="$emit('refresh-details')" class="refresh-btn" title="Refresh details">
        🔄
      </button>
    </div>
    
    <div v-if="conversation" class="details-content">
      <!-- Basic Information -->
      <div class="detail-section">
        <h4>Basic Information</h4>
        <div class="info-grid">
          <div class="info-item">
            <label>User Number:</label>
            <input v-model="details.user_number" readonly class="info-input readonly" />
          </div>
          <div class="info-item">
            <label>User Name:</label>
            <input v-model="details.user_name" @blur="updateUserInfo" class="info-input" />
          </div>
          <div class="info-item">
            <label>Bot Name:</label>
            <input v-model="details.bot_name" @blur="updateBotName" class="info-input" />
          </div>
        </div>
      </div>
      
      <!-- Conversation Settings -->
      <div class="detail-section">
        <h4>Conversation Settings</h4>
        <div class="settings-grid">
          <div class="setting-item">
            <label>Persona:</label>
            <select v-model="details.persona" @change="updatePersona" class="setting-select">
              <option v-for="persona in personas" :key="persona" :value="persona">
                {{ persona }}
              </option>
            </select>
          </div>
          
          <div class="setting-item">
            <label>Mode:</label>
            <select v-model="details.convmode" @change="updateConvMode" class="setting-select">
              <option v-for="mode in convmodes" :key="mode" :value="mode">
                {{ mode }}
              </option>
            </select>
          </div>
          
          <div class="setting-item">
            <label>Type:</label>
            <select v-model="details.convtype" @change="updateConvType" class="setting-select">
              <option v-for="type in convtypes" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
          </div>
          
          <div class="setting-item">
            <label>Interval (sec):</label>
            <input v-model.number="details.interval" @blur="updateInterval" class="setting-input" type="number" />
          </div>
          
          <div class="setting-item">
            <label>Temperature:</label>
            <input v-model.number="details.temperature" @blur="updateTemperature" step="0.1" class="setting-input" type="number" />
          </div>
        </div>
      </div>
      
      <!-- Usage Limits -->
      <div class="detail-section">
        <h4>Usage Limits</h4>
        <div class="usage-controls">
          <div class="usage-item">
            <label>Free Tries:</label>
            <div class="usage-input-group">
              <input v-model.number="usage.free_tries" type="number" class="usage-input" />
              <button @click="addFreeTries" class="usage-btn">Add</button>
            </div>
          </div>
          
          <div class="usage-item">
            <label>Paid Messages:</label>
            <div class="usage-input-group">
              <input v-model.number="usage.paid_messages" type="number" class="usage-input" />
              <button @click="addPaidMessages" class="usage-btn">Add</button>
            </div>
          </div>
          
          <div class="usage-item">
            <label>Free GPT:</label>
            <button 
              @click="toggleFreeGpt" 
              :class="['toggle-btn', { active: usage.free_gpt }]"
              class="toggle-btn"
            >
              {{ usage.free_gpt ? 'Enabled' : 'Disabled' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- Message Content -->
      <div class="detail-section">
        <h4>Message Content</h4>
        <div class="message-controls">
          <div class="message-item">
            <label>System Message:</label>
            <textarea v-model="messages.system" rows="3" class="message-textarea"></textarea>
            <button @click="setSystemMessage" class="message-btn">Set</button>
          </div>
          
          <div class="message-item">
            <label>User Message:</label>
            <textarea v-model="messages.user" rows="3" class="message-textarea"></textarea>
            <button @click="setUserMessage" class="message-btn">Set</button>
          </div>
          
          <div class="message-item">
            <label>Assistant Message:</label>
            <textarea v-model="messages.assistant" rows="3" class="message-textarea"></textarea>
            <button @click="setAssistantMessage" class="message-btn">Set</button>
          </div>
        </div>
      </div>
      
      <!-- Interview Settings -->
      <div class="detail-section">
        <h4>Interview Settings</h4>
        <div class="interview-controls">
          <div class="interview-item">
            <label>Intro Message:</label>
            <textarea v-model="interview.intro" rows="2" class="interview-textarea"></textarea>
          </div>
          
          <div class="interview-item">
            <label>Outro Message:</label>
            <textarea v-model="interview.outro" rows="2" class="interview-textarea"></textarea>
          </div>
          
          <button @click="setInterviewMessages" class="interview-btn">Set Interview Messages</button>
        </div>
      </div>
      
      <!-- Direct Communication -->
      <div class="detail-section">
        <h4>Direct Communication</h4>
        <div class="communication-controls">
          <textarea 
            v-model="directMessage" 
            placeholder="Type message to send..." 
            rows="3" 
            class="direct-textarea"
          ></textarea>
          <button @click="sendDirectMessage" class="direct-btn">Send Message</button>
        </div>
      </div>
      
      <!-- Quick Actions -->
      <div class="detail-section">
        <h4>Quick Actions</h4>
        <div class="action-buttons">
          <button @click="resetChannel" class="action-btn reset">Reset Channel</button>
          <button @click="testSend" class="action-btn test">Test Send</button>
          <button @click="startQuestioning" class="action-btn question">Start Questions</button>
          <button @click="resetQuestions" class="action-btn reset-questions">Reset Questions</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { adminApi } from '@/api/client'
import { Persona, ConvMode, ConvType, Role } from '@/types'
import type { Conversation } from '@/types'

const props = defineProps<{
  conversation: Conversation
}>()

const emit = defineEmits(['update-setting', 'refresh-details'])

const details = reactive({
  user_number: '',
  user_name: '',
  bot_name: '',
  persona: Persona.ASSISTANT,
  convmode: ConvMode.CHITCHAT,
  convtype: ConvType.DEMO,
  interval: 600,
  temperature: 0.7
})

const usage = reactive({
  free_tries: 0,
  paid_messages: 0,
  free_gpt: false
})

const messages = reactive({
  system: '',
  user: '',
  assistant: ''
})

const interview = reactive({
  intro: '',
  outro: ''
})

const directMessage = ref('')

const personas = Object.values(Persona)
const convmodes = Object.values(ConvMode)
const convtypes = Object.values(ConvType)

// Load conversation details
const loadConversationDetails = () => {
  if (!props.conversation) return
  
  Object.assign(details, {
    user_number: props.conversation.user_number,
    user_name: props.conversation.user_name || '',
    bot_name: props.conversation.bot_name || '',
    persona: props.conversation.persona,
    convmode: props.conversation.convmode,
    convtype: props.conversation.convtype,
    interval: props.conversation.interval,
    temperature: props.conversation.temperature
  })
  
  Object.assign(usage, {
    free_tries: props.conversation.free_tries,
    paid_messages: props.conversation.paid_messages,
    free_gpt: props.conversation.free_gpt
  })
  
  // Load messages
  if (props.conversation.messages && props.conversation.messages.length >= 3) {
    Object.assign(messages, {
      system: props.conversation.messages[0]?.content || '',
      user: props.conversation.messages[1]?.content || '',
      assistant: props.conversation.messages[2]?.content || ''
    })
  }
  
  Object.assign(interview, {
    intro: props.conversation.intro_msg || '',
    outro: props.conversation.outro_msg || ''
  })
}

// Update functions
const updatePersona = () => {
  emit('update-setting', { type: 'persona', value: details.persona, userNumber: details.user_number })
}

const updateConvMode = () => {
  emit('update-setting', { type: 'convmode', value: details.convmode, userNumber: details.user_number })
}

const updateConvType = () => {
  emit('update-setting', { type: 'convtype', value: details.convtype, userNumber: details.user_number })
}

const updateInterval = () => {
  emit('update-setting', { type: 'interval', value: details.interval, userNumber: details.user_number })
}

const updateTemperature = () => {
  emit('update-setting', { type: 'temperature', value: details.temperature, userNumber: details.user_number })
}

const updateUserInfo = async () => {
  try {
    await adminApi.setBotName(details.user_number, details.bot_name)
    console.log('User info updated')
  } catch (error) {
    console.error('Failed to update user info:', error)
  }
}

const updateBotName = async () => {
  try {
    await adminApi.setBotName(details.user_number, details.bot_name)
    console.log('Bot name updated')
  } catch (error) {
    console.error('Failed to update bot name:', error)
  }
}

const setSystemMessage = async () => {
  try {
    await adminApi.setSystemMessage(details.user_number, messages.system)
    console.log('System message updated')
  } catch (error) {
    console.error('Failed to set system message:', error)
  }
}

const setUserMessage = async () => {
  try {
    await adminApi.setUserMessage(details.user_number, messages.user)
    console.log('User message updated')
  } catch (error) {
    console.error('Failed to set user message:', error)
  }
}

const setAssistantMessage = async () => {
  try {
    await adminApi.setAssistantMessage(details.user_number, messages.assistant)
    console.log('Assistant message updated')
  } catch (error) {
    console.error('Failed to set assistant message:', error)
  }
}

const setInterviewMessages = async () => {
  try {
    await adminApi.setInterviewMessages(details.user_number, interview.intro, interview.outro)
    console.log('Interview messages updated')
  } catch (error) {
    console.error('Failed to set interview messages:', error)
  }
}

const addFreeTries = async () => {
  try {
    const unit = 10 // Default add 10 tries
    await adminApi.addFreeTries(details.user_number, unit)
    usage.free_tries += unit
    console.log(`Added ${unit} free tries`)
  } catch (error) {
    console.error('Failed to add free tries:', error)
  }
}

const addPaidMessages = async () => {
  try {
    const unit = 10 // Default add 10 messages
    await adminApi.addPaidMessages(details.user_number, unit)
    usage.paid_messages += unit
    console.log(`Added ${unit} paid messages`)
  } catch (error) {
    console.error('Failed to add paid messages:', error)
  }
}

const toggleFreeGpt = async () => {
  try {
    await adminApi.toggleFreeGpt(details.user_number)
    usage.free_gpt = !usage.free_gpt
    console.log(`Free GPT toggled: ${usage.free_gpt}`)
  } catch (error) {
    console.error('Failed to toggle free GPT:', error)
  }
}

const sendDirectMessage = async () => {
  if (!directMessage.value.trim()) return
  
  try {
    await adminApi.sendMessage(details.user_number, directMessage.value)
    directMessage.value = ''
    console.log('Message sent successfully')
  } catch (error) {
    console.error('Failed to send message:', error)
  }
}

const resetChannel = async () => {
  try {
    await adminApi.resetChannel(details.user_number)
    console.log('Channel reset')
    emit('refresh-details')
  } catch (error) {
    console.error('Failed to reset channel:', error)
  }
}

const testSend = async () => {
  try {
    const response = await adminApi.testSend(details.user_number)
    console.log('Test send response:', response.data)
  } catch (error) {
    console.error('Test send failed:', error)
  }
}

const startQuestioning = async () => {
  try {
    await adminApi.startQuestioning(details.user_number)
    console.log('Questioning started')
  } catch (error) {
    console.error('Failed to start questioning:', error)
  }
}

const resetQuestions = async () => {
  try {
    await adminApi.resetBotQuestions(details.user_number)
    console.log('Questions reset')
  } catch (error) {
    console.error('Failed to reset questions:', error)
  }
}

// Watch for conversation changes
watch(() => props.conversation, loadConversationDetails, { immediate: true })
</script>

<style scoped>
.conversation-details {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.details-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.refresh-btn {
  padding: 8px 12px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.refresh-btn:hover {
  background: #e5e7eb;
}

.detail-section {
  margin-bottom: 32px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  border-bottom: 2px solid #e5e7eb;
  padding-bottom: 8px;
}

.info-grid, .settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.info-item, .setting-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-item label, .setting-item label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-input, .setting-input {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.info-input:focus, .setting-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.info-input.readonly {
  background: #f9fafb;
  color: #6b7280;
}

.setting-select {
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.usage-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.usage-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.usage-item label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.usage-input-group {
  display: flex;
  gap: 8px;
}

.usage-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.usage-btn {
  padding: 8px 12px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.usage-btn:hover {
  background: #2563eb;
}

.toggle-btn {
  padding: 8px 16px;
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toggle-btn.active {
  background: #10b981;
  color: white;
  border-color: #10b981;
}

.message-controls {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-item label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.message-textarea {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
}

.message-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.message-btn {
  align-self: flex-start;
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.message-btn:hover {
  background: #2563eb;
}

.interview-controls {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.interview-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.interview-item label {
  font-size: 12px;
  font-weight: 600;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.interview-textarea {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
}

.interview-btn {
  align-self: flex-start;
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.interview-btn:hover {
  background: #2563eb;
}

.communication-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.direct-textarea {
  padding: 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  resize: vertical;
}

.direct-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.direct-btn {
  align-self: flex-start;
  padding: 8px 16px;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.direct-btn:hover {
  background: #059669;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.action-btn {
  padding: 8px 16px;
  border: 1px solid #d1d5db;
  background: white;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  border-color: #9ca3af;
  background: #f8fafc;
}

.action-btn.reset {
  border-color: #f59e0b;
  color: #d97706;
}

.action-btn.test {
  border-color: #10b981;
  color: #059669;
}

.action-btn.question {
  border-color: #3b82f6;
  color: #2563eb;
}

.action-btn.reset-questions {
  border-color: #ef4444;
  color: #dc2626;
}

@media (max-width: 768px) {
  .details-header {
    flex-direction: column;
    gap: 12px;
  }
  
  .info-grid, .settings-grid, .usage-controls {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .action-btn {
    width: 100%;
  }
}
</style>