<template>
  <div class="quick-actions">
    <div class="actions-header">
      <h3>Quick Actions</h3>
    </div>
    
    <div class="actions-grid">
      <button 
        @click="$emit('refresh-data')"
        :disabled="loading"
        class="action-btn refresh"
      >
        <div class="btn-icon">🔄</div>
        <div class="btn-content">
          <span class="btn-title">Refresh Data</span>
          <span class="btn-desc">Reload all conversations</span>
        </div>
      </button>
      
      <button 
        @click="$emit('save-logs')"
        :disabled="loading"
        class="action-btn save"
      >
        <div class="btn-icon">💾</div>
        <div class="btn-content">
          <span class="btn-title">Save Logs</span>
          <span class="btn-desc">Export conversation logs</span>
        </div>
      </button>
      
      <button 
        @click="$emit('rebuild-db')"
        :disabled="loading"
        class="action-btn rebuild"
      >
        <div class="btn-icon">🔧</div>
        <div class="btn-content">
          <span class="btn-title">Rebuild DB</span>
          <span class="btn-desc">Rebuild connection database</span>
        </div>
      </button>
      
      <button 
        @click="pingServer"
        :disabled="loading"
        class="action-btn ping"
      >
        <div class="btn-icon">🔍</div>
        <div class="btn-content">
          <span class="btn-title">Ping Server</span>
          <span class="btn-desc">Test server connectivity</span>
        </div>
      </button>
    </div>
    
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <span>Processing...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { adminApi } from '@/api/client'

const props = defineProps<{
  loading: boolean
}>()

const emit = defineEmits(['refresh-data', 'save-logs', 'rebuild-db'])

const pingServer = async () => {
  try {
    const response = await adminApi.ping()
    console.log('Server ping response:', response.data)
    
    // Show a simple notification
    const notification = document.createElement('div')
    notification.className = 'ping-notification success'
    notification.textContent = `Server response: ${response.data.message}`
    document.body.appendChild(notification)
    
    setTimeout(() => {
      document.body.removeChild(notification)
    }, 3000)
  } catch (error) {
    console.error('Ping failed:', error)
    
    const notification = document.createElement('div')
    notification.className = 'ping-notification error'
    notification.textContent = 'Server ping failed'
    document.body.appendChild(notification)
    
    setTimeout(() => {
      document.body.removeChild(notification)
    }, 3000)
  }
}
</script>

<style scoped>
.quick-actions {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
  position: relative;
}

.actions-header h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.action-btn:hover:not(:disabled) {
  border-color: #9ca3af;
  background: #f9fafb;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-icon {
  font-size: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #f3f4f6;
  border-radius: 8px;
  flex-shrink: 0;
}

.btn-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.btn-title {
  font-weight: 600;
  color: #1f2937;
  font-size: 14px;
}

.btn-desc {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.3;
}

.action-btn.refresh .btn-icon { background: #dbeafe; }
.action-btn.save .btn-icon { background: #dcfce7; }
.action-btn.rebuild .btn-icon { background: #fef3c7; }
.action-btn.ping .btn-icon { background: #fce7f3; }

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  border-radius: 12px;
  z-index: 10;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-top: 2px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Toast notifications */
:global(.ping-notification) {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  animation: slideIn 0.3s ease;
}

:global(.ping-notification.success) {
  background: #22c55e;
}

:global(.ping-notification.error) {
  background: #ef4444;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .actions-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .action-btn {
    padding: 12px;
  }
  
  .btn-icon {
    width: 32px;
    height: 32px;
    font-size: 20px;
  }
  
  .btn-title {
    font-size: 13px;
  }
  
  .btn-desc {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>