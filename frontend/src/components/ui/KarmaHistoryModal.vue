<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        @click.self="$emit('update:modelValue', false)"
      >
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-lg max-h-[85vh] flex flex-col">

          <!-- Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
            <div class="flex items-center gap-3">
              <span class="text-2xl">⭐</span>
              <div>
                <h3 class="text-lg font-bold text-gray-900 dark:text-white">Історія карми</h3>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ username }}</p>
              </div>
            </div>
            <button
              @click="$emit('update:modelValue', false)"
              class="p-2 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <!-- Loading -->
          <div v-if="loading" class="flex-1 flex items-center justify-center py-12">
            <div class="animate-spin rounded-full h-10 w-10 border-4 border-gray-200 border-t-purple-500"></div>
          </div>

          <!-- Empty -->
          <div v-else-if="!history.length" class="flex-1 flex flex-col items-center justify-center py-12 text-center">
            <span class="text-5xl mb-3">🌱</span>
            <p class="text-gray-500 dark:text-gray-400">Ще немає записів карми</p>
          </div>

          <!-- List -->
          <div v-else class="flex-1 overflow-y-auto px-6 py-2">
            <TransitionGroup name="list" tag="div" class="space-y-2 py-2">
              <div
                v-for="(item, index) in history"
                :key="index"
                class="flex items-center justify-between p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <!-- Points badge -->
                <div class="flex items-center gap-3">
                  <div
                    class="w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0"
                    :class="item.points > 0
                      ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400'
                      : 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400'"
                  >
                    {{ item.points > 0 ? '+' + item.points : item.points }}
                  </div>
                  <div>
                    <p class="text-sm text-gray-800 dark:text-gray-200">{{ item.reason }}</p>
                    <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ formatDate(item.created_at) }}</p>
                  </div>
                </div>
              </div>
            </TransitionGroup>
          </div>

          <!-- Pagination -->
          <div
            v-if="totalPages > 1"
            class="flex items-center justify-between px-6 py-3 border-t border-gray-200 dark:border-gray-700 flex-shrink-0"
          >
            <p class="text-xs text-gray-500 dark:text-gray-400">
              Сторінка {{ currentPage }} з {{ totalPages }}
            </p>
            <div class="flex items-center gap-1">
              <button
                @click="changePage(currentPage - 1)"
                :disabled="currentPage === 1"
                class="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeftIcon class="w-4 h-4" />
              </button>

              <!-- Page numbers -->
              <template v-for="page in visiblePages" :key="page">
                <span v-if="page === '...'" class="px-2 text-gray-400 text-sm">…</span>
                <button
                  v-else
                  @click="changePage(page)"
                  class="w-8 h-8 rounded-lg text-sm font-medium transition-colors"
                  :class="page === currentPage
                    ? 'bg-purple-600 text-white'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'"
                >
                  {{ page }}
                </button>
              </template>

              <button
                @click="changePage(currentPage + 1)"
                :disabled="currentPage === totalPages"
                class="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRightIcon class="w-4 h-4" />
              </button>
            </div>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { XMarkIcon, ChevronLeftIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'
import { format } from 'date-fns'
import { uk } from 'date-fns/locale'
import api from '@/services/api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  username: { type: String, required: true }
})

const emit = defineEmits(['update:modelValue'])

const history = ref([])
const loading = ref(false)
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 10

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize))

// Генерація видимих сторінок з "..."
const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const pages = []

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
      pages.push(i)
    }
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }

  return pages
})

const fetchHistory = async (page = 1) => {
  loading.value = true
  try {
    const { data } = await api.get(`/karma/my_history/`, {
      params: { page, page_size: pageSize }
    })
    history.value = data.results
    totalCount.value = data.count
    currentPage.value = page
  } catch (error) {
    console.error('Error fetching karma history:', error)
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  fetchHistory(page)
}

const formatDate = (dateString) => {
  try {
    return format(new Date(dateString), 'd MMM yyyy, HH:mm', { locale: uk })
  } catch {
    return dateString
  }
}

// Завантажуємо при відкритті
watch(() => props.modelValue, (val) => {
  if (val) {
    currentPage.value = 1
    fetchHistory(1)
  }
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-active .bg-white,
.modal-enter-active .dark\:bg-gray-800,
.modal-leave-active .bg-white,
.modal-leave-active .dark\:bg-gray-800 {
  transition: transform 0.25s ease;
}
.modal-enter-from .bg-white,
.modal-leave-to .bg-white {
  transform: scale(0.95) translateY(10px);
}

.list-enter-active,
.list-leave-active {
  transition: all 0.2s ease;
}
.list-enter-from {
  opacity: 0;
  transform: translateX(-10px);
}
.list-leave-to {
  opacity: 0;
  transform: translateX(10px);
}
</style>