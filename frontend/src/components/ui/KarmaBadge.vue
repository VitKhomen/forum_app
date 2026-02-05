<!-- components/ui/KarmaBadge.vue -->
<template>
  <div class="karma-badge" :class="size">
    <span class="icon">⭐</span>
    <span class="value">{{ karma }}</span>
    <span v-if="showLevel" class="level">lvl {{ level }}</span>
  </div>
</template>

<script setup>
defineProps({
  karma: {
    type: Number,
    default: 0
  },
  level: {
    type: Number,
    default: 1
  },
  size: {
    type: String,
    default: 'medium', // small, medium, large
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  showLevel: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
.karma-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  color: white;
  font-weight: 600;
  white-space: nowrap;
}

.karma-badge.small {
  padding: 2px 8px;
  font-size: 0.85em;
  gap: 4px;
}

.karma-badge.large {
  padding: 8px 16px;
  font-size: 1.1em;
  gap: 8px;
}

.icon { font-size: 1em; }
.value { font-size: 1em; }
.level { 
  font-size: 0.85em; 
  opacity: 0.9; 
  margin-left: 2px;
}
</style>