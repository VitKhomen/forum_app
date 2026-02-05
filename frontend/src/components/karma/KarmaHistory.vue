<!-- components/karma/KarmaHistory.vue -->
<template>
  <div class="karma-history">
    <div class="header">
      <h3>Історія карми</h3>
      <button v-if="canLoadMore" @click="loadMore" class="load-more">
        Показати більше
      </button>
    </div>

    <div v-if="loading && items.length === 0" class="loading">
      Завантаження...
    </div>

    <div v-else-if="items.length === 0" class="empty">
      <p>📊 Історія порожня</p>
      <p class="hint">Створюй пости і коментарі щоб заробляти карму!</p>
    </div>

    <div v-else class="history-list">
      <TransitionGroup name="list">
        <div 
          v-for="item in items" 
          :key="item.created_at"
          class="history-item"
          :class="{ positive: item.points > 0, negative: item.points < 0 }"
        >
          <div class="points">
            {{ item.points > 0 ? '+' : '' }}{{ item.points }}
          </div>
          <div class="details">
            <div class="reason">{{ item.reason }}</div>
            <div class="date">{{ formatDate(item.created_at) }}</div>
          </div>
        </div>
      </TransitionGroup>
    </div>

    <div v-if="loading && items.length > 0" class="loading-more">
      Завантаження...
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useKarma } from '@/composables/useKarma'

const props = defineProps({
  userId: {
    type: Number,
    default: null // null = текущий пользователь
  },
  limit: {
    type: Number,
    default: 10
  },
  showLoadMore: {
    type: Boolean,
    default: true
  }
})

const { getKarmaHistory, formatDate } = useKarma()

const items = ref([])
const loading = ref(false)
const hasMore = ref(true)
const page = ref(1)

const canLoadMore = computed(() => 
  props.showLoadMore && hasMore.value && !loading.value
)

const loadHistory = async () => {
  if (loading.value) return
  
  loading.value = true
  try {
    const newItems = await getKarmaHistory(props.userId, {
      limit: props.limit,
      page: page.value
    })
    
    if (newItems.length < props.limit) {
      hasMore.value = false
    }
    
    items.value = [...items.value, ...newItems]
  } catch (error) {
    console.error('Помилка завантаження історії:', error)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  page.value++
  loadHistory()
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.karma-history {
  background: white;
  border-radius: 12px;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.load-more {
  padding: 6px 12px;
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
}

.load-more:hover {
  background: #e0e0e0;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: #f8f9fa;
  border-left: 3px solid #ddd;
}

.history-item.positive {
  border-left-color: #28a745;
  background: #f0fdf4;
}

.history-item.negative {
  border-left-color: #dc3545;
  background: #fef2f2;
}

.points {
  font-weight: bold;
  font-size: 1.2em;
  min-width: 50px;
}

.positive .points { color: #28a745; }
.negative .points { color: #dc3545; }

.details {
  flex: 1;
}

.reason {
  font-weight: 500;
  margin-bottom: 4px;
}

.date {
  font-size: 0.85em;
  color: #6c757d;
}

.empty {
  text-align: center;
  padding: 40px 20px;
  color: #6c757d;
}

.hint {
  font-size: 0.9em;
  margin-top: 8px;
}

.loading, .loading-more {
  text-align: center;
  padding: 20px;
  color: #6c757d;
}

/* Анимация списка */
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>