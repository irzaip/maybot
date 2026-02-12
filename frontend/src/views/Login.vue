<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>MayBot Admin</h1>
        <p>WhatsApp Bot Administration Panel</p>
      </div>
      
      <div class="login-form">
        <div class="form-group">
          <label for="admin_key">Admin Key:</label>
          <input 
            id="admin_key"
            v-model="adminKey" 
            type="password" 
            placeholder="Enter admin phone number"
            class="form-input"
            @keyup.enter="login"
          />
        </div>
        
        <div class="form-actions">
          <button 
            @click="login" 
            :disabled="loading || !adminKey"
            class="login-button"
          >
            <span v-if="loading">Connecting...</span>
            <span v-else>Access Admin Panel</span>
          </button>
        </div>
        
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const adminKey = ref('')
const loading = ref(false)
const error = ref('')

onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search)
  const existingKey = urlParams.get('admin_key')
  if (existingKey) {
    adminKey.value = existingKey
  }
})

const login = async () => {
  if (!adminKey.value.trim()) {
    error.value = 'Please enter an admin key'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch(`/api/admin/dashboard/stats?admin_key=${encodeURIComponent(adminKey.value)}`)
    if (response.ok) {
      window.location.href = `/admin?admin_key=${encodeURIComponent(adminKey.value)}`
    } else {
      error.value = 'Invalid admin key. Access denied.'
    }
  } catch (err) {
    error.value = 'Connection failed. Please check the server.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.login-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  color: #333;
  font-size: 28px;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.login-header p {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-actions {
  margin-bottom: 20px;
}

.login-button {
  width: 100%;
  padding: 14px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: #fee;
  color: #c53030;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
}

@media (max-width: 480px) {
  .login-card {
    padding: 30px 20px;
  }
}
</style>