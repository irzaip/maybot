<template>
  <div class="error-notification" @click="$emit('dismiss')">
    <div class="error-content">
      <div class="error-icon">⚠️</div>
      <div class="error-message">{{ error }}</div>
      <button class="error-close" @click.stop="$emit('dismiss')">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  error: string
}>()

defineEmits(['dismiss'])
</script>

<style scoped>
.error-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.15);
  z-index: 1000;
  max-width: 400px;
  cursor: pointer;
  animation: slideIn 0.3s ease;
}

.error-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.error-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.error-message {
  flex: 1;
  color: #991b1b;
  font-weight: 500;
  font-size: 14px;
  line-height: 1.4;
}

.error-close {
  background: none;
  border: none;
  color: #991b1b;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.error-close:hover {
  background: #fee2e2;
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
  .error-notification {
    top: 10px;
    right: 10px;
    left: 10px;
    max-width: none;
  }
  
  .error-message {
    font-size: 13px;
  }
}
</style>