<template>
  <div class="system-status">
    <div class="status-header">
      <h2>System Status</h2>
      <div class="status-indicators">
        <div 
          class="status-indicator"
          :class="{ 
            online: stats.server_status === 'online',
            offline: stats.server_status === 'offline',
            maintenance: stats.maintenance_mode 
          }"
        >
          <div class="status-dot"></div>
          <span>{{ statusText }}</span>
        </div>
      </div>
    </div>
    
    <div class="status-grid">
      <div class="status-card">
        <div class="card-header">
          <h3>Conversations</h3>
          <i class="icon-users"></i>
        </div>
        <div class="card-value">{{ stats.active_conversations }}</div>
        <div class="card-label">Active Conversations</div>
      </div>
      
      <div class="status-card">
        <div class="card-header">
          <h3>Messages</h3>
          <i class="icon-messages"></i>
        </div>
        <div class="card-value">{{ formatNumber(stats.total_messages) }}</div>
        <div class="card-label">Total Messages</div>
      </div>
      
      <div class="status-card">
        <div class="card-header">
          <h3>Token Usage</h3>
          <i class="icon-token"></i>
        </div>
        <div class="card-value">{{ formatNumber(stats.token_usage) }}</div>
        <div class="card-label">Tokens Used</div>
      </div>
      
      <div class="status-card">
        <div class="card-header">
          <h3>Maintenance</h3>
          <i class="icon-settings"></i>
        </div>
        <div class="card-value">
          {{ stats.maintenance_mode ? 'ON' : 'OFF' }}
        </div>
        <div class="card-label">Maintenance Mode</div>
      </div>
    </div>
    
    <div class="status-actions">
      <button 
        @click="$emit('toggle-maintenance')"
        :class="['maintenance-btn', { active: stats.maintenance_mode }]"
        class="action-btn"
      >
        <i class="icon-wrench"></i>
        {{ stats.maintenance_mode ? 'Disable Maintenance' : 'Enable Maintenance' }}
      </button>
      
      <div class="last-updated">
        Last updated: {{ lastUpdated }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { DashboardStats } from '@/types'

const props = defineProps<{
  stats: DashboardStats
}>()

const emit = defineEmits(['toggle-maintenance'])

const statusText = computed(() => {
  if (props.stats.maintenance_mode) return 'Maintenance'
  if (props.stats.server_status === 'online') return 'Online'
  return 'Offline'
})

const lastUpdated = computed(() => {
  return new Date().toLocaleTimeString()
})

const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  return num.toString()
}
</script>

<style scoped>
.system-status {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  margin-bottom: 24px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.status-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-indicator.online {
  background: #dcfce7;
  color: #16a34a;
}

.status-indicator.online .status-dot {
  background: #22c55e;
}

.status-indicator.offline {
  background: #fee2e2;
  color: #dc2626;
}

.status-indicator.offline .status-dot {
  background: #ef4444;
}

.status-indicator.maintenance {
  background: #fef3c7;
  color: #d97706;
}

.status-indicator.maintenance .status-dot {
  background: #f59e0b;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.status-card {
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.card-header h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #6b7280;
}

.card-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 4px;
}

.card-label {
  font-size: 12px;
  color: #9ca3af;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.maintenance-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: 2px solid #d1d5db;
  background: white;
  border-radius: 8px;
  font-weight: 600;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}

.maintenance-btn:hover {
  border-color: #9ca3af;
  background: #f9fafb;
}

.maintenance-btn.active {
  border-color: #dc2626;
  background: #fef2f2;
  color: #dc2626;
}

.maintenance-btn.active:hover {
  background: #fee2e2;
}

.last-updated {
  font-size: 12px;
  color: #9ca3af;
}

/* Icons */
.icon-users::before { content: "👥"; }
.icon-messages::before { content: "💬"; }
.icon-token::before { content: "🎯"; }
.icon-settings::before { content: "⚙️"; }
.icon-wrench::before { content: "🔧"; }

@media (max-width: 768px) {
  .status-header {
    flex-direction: column;
    gap: 12px;
    text-align: center;
  }
  
  .status-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .status-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .maintenance-btn {
    justify-content: center;
  }
}
</style>