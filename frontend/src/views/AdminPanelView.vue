<template>
  <div class="max-w-5xl mx-auto space-y-6">

    <!-- Заголовок -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          🛡️ Панель модерації
        </h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Черга скарг від користувачів
        </p>
      </div>

      <!-- Лічильник pending -->
      <div
        v-if="pendingCount > 0"
        class="px-4 py-2 bg-orange-100 dark:bg-orange-900/30 text-orange-700
               dark:text-orange-400 rounded-xl text-sm font-semibold"
      >
        {{ pendingCount }} нових скарг
      </div>
    </div>

    <!-- Таби: pending / resolved / rejected -->
    <div class="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-xl p-1">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        @click="switchTab(tab.value)"
        class="flex-1 py-2 rounded-lg text-sm font-medium transition-all"
        :class="activeTab === tab.value
          ? 'bg-white dark:bg-gray-700 shadow text-gray-900 dark:text-white'
          : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
      >
        {{ tab.label }}
        <span
          v-if="tab.value === 'pending' && pendingCount"
          class="ml-1.5 px-1.5 py-0.5 bg-orange-500 text-white text-xs rounded-full"
        >
          {{ pendingCount }}
        </span>
      </button>
    </div>

    <!-- Скелетон -->
    <div v-if="loading" class="space-y-3">
      <div
        v-for="i in 5" :key="i"
        class="h-24 bg-gray-100 dark:bg-gray-800 rounded-xl animate-pulse"
      />
    </div>

    <!-- Порожньо -->
    <div
      v-else-if="!reports.length"
      class="text-center py-20 bg-gray-50 dark:bg-gray-900 rounded-2xl"
    >
      <p class="text-4xl mb-3">✅</p>
      <p class="text-gray-500 dark:text-gray-400 font-medium">
        {{ activeTab === 'pending' ? 'Нових скарг немає' : 'Записів немає' }}
      </p>
    </div>

    <!-- Список репортів -->
    <div v-else class="space-y-3">
      <div
        v-for="report in reports"
        :key="report.id"
        class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200
               dark:border-gray-700 p-5 shadow-sm"
      >
        <div class="flex flex-col sm:flex-row sm:items-start gap-4">

          <!-- Ліва частина: інфо про репорт -->
          <div class="flex-1 min-w-0">
            <!-- Тип + id обʼєкта -->
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <span
                class="px-2 py-0.5 rounded-full text-xs font-semibold"
                :class="report.content_type_name === 'post'
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                  : 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400'"
              >
                {{ report.content_type_name === 'post' ? '📝 Пост' : '💬 Коментар' }}
              </span>

              <span class="px-2 py-0.5 rounded-full text-xs font-semibold"
                :class="{
                  'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400': report.status === 'pending',
                  'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400': report.status === 'resolved',
                  'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400': report.status === 'rejected',
                }"
              >
                {{ report.status_display }}
              </span>

              <span class="text-xs text-gray-400">
                {{ report.reason_display }}
              </span>
            </div>

            <!-- Превʼю скаржного контенту -->
            <p class="text-sm font-medium text-gray-900 dark:text-white mb-1 line-clamp-2">
              {{ report.object_preview }}
            </p>

            <div class="flex flex-wrap gap-3 text-xs text-gray-500 dark:text-gray-400 mt-2">
              <span>
                Автор контенту:
                <RouterLink
                  :to="`/users/${report.object_author}`"
                  class="text-blue-600 dark:text-blue-400 hover:underline font-medium"
                >
                  @{{ report.object_author }}
                </RouterLink>
              </span>
              <span>
                Скарга від:
                <span class="font-medium text-gray-700 dark:text-gray-300">
                  @{{ report.reporter_username }}
                </span>
              </span>
              <span>{{ formatDate(report.created_at) }}</span>
            </div>

            <!-- Коментар юзера до скарги -->
            <p
              v-if="report.comment"
              class="mt-2 text-sm text-gray-600 dark:text-gray-400 italic
                     bg-gray-50 dark:bg-gray-700/50 rounded-lg px-3 py-2"
            >
              "{{ report.comment }}"
            </p>

            <!-- Нотатка адміна (якщо вже оброблено) -->
            <p
              v-if="report.admin_note && report.status !== 'pending'"
              class="mt-2 text-xs text-gray-500 dark:text-gray-400"
            >
              Адмін: {{ report.admin_note }}
            </p>
          </div>

          <!-- Права частина: посилання + дії -->
          <div class="flex flex-col gap-2 flex-shrink-0 min-w-[140px]">

            <!-- Посилання на контент -->
            <RouterLink
              :to="contentLink(report)"
              target="_blank"
              class="text-center px-3 py-1.5 border border-gray-200 dark:border-gray-600
                     text-gray-700 dark:text-gray-300 rounded-lg text-xs
                     hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Переглянути →
            </RouterLink>

            <!-- Дії тільки для pending -->
            <template v-if="report.status === 'pending'">
              <!-- Адмін-нотатка -->
              <input
                v-model="adminNotes[report.id]"
                type="text"
                placeholder="Нотатка (опц.)"
                class="px-2 py-1.5 text-xs border border-gray-200 dark:border-gray-600
                       rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300
                       focus:outline-none focus:ring-1 focus:ring-blue-400"
              />

              <button
                @click="handleResolve(report)"
                :disabled="actionLoading[report.id]"
                class="px-3 py-1.5 bg-red-500 hover:bg-red-600 text-white rounded-lg
                       text-xs font-medium transition-colors disabled:opacity-50"
              >
                🗑 Видалити контент
              </button>

              <button
                @click="handleReject(report)"
                :disabled="actionLoading[report.id]"
                class="px-3 py-1.5 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300
                       dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300
                       rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
              >
                ✓ Залишити
              </button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Пагінація -->
    <div v-if="totalPages > 1" class="flex justify-center gap-2">
      <button
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
        class="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700
               text-sm disabled:opacity-40 hover:bg-gray-50 dark:hover:bg-gray-800 transition"
      >
        ← Назад
      </button>
      <span class="px-4 py-2 text-sm text-gray-600 dark:text-gray-400">
        {{ currentPage }} / {{ totalPages }}
      </span>
      <button
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
        class="px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700
               text-sm disabled:opacity-40 hover:bg-gray-50 dark:hover:bg-gray-800 transition"
      >
        Далі →
      </button>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { moderationAPI } from '@/services/api'
import { useToast } from 'vue-toastification'
import { format } from 'date-fns'
import { uk } from 'date-fns/locale'

const authStore = useAuthStore()
const router    = useRouter()
const toast     = useToast()

// Перенаправити якщо не адмін
onMounted(() => {
  if (!authStore.user?.is_staff) {
    router.replace('/')
  } else {
    fetchReports()
    fetchStats()
  }
})

const tabs = [
  { value: 'pending',  label: 'Нові' },
  { value: 'resolved', label: 'Видалено' },
  { value: 'rejected', label: 'Відхилено' },
]

const activeTab    = ref('pending')
const reports      = ref([])
const loading      = ref(false)
const currentPage  = ref(1)
const totalCount   = ref(0)
const pendingCount = ref(0)
const adminNotes   = ref({})     // { [report_id]: 'нотатка' }
const actionLoading = ref({})    // { [report_id]: true/false }

const PAGE_SIZE  = 20
const totalPages = computed(() => Math.ceil(totalCount.value / PAGE_SIZE))

const fetchStats = async () => {
  try {
    const { data } = await moderationAPI.getStats()
    pendingCount.value = data.pending_count
  } catch {}
}

const fetchReports = async () => {
  loading.value = true
  try {
    const { data } = await moderationAPI.getQueue({
      status:    activeTab.value,
      page:      currentPage.value,
      page_size: PAGE_SIZE,
    })
    reports.value    = data.results || []
    totalCount.value = data.count   || 0
  } catch {
    toast.error('Помилка завантаження')
  } finally {
    loading.value = false
  }
}

const switchTab = (tab) => {
  activeTab.value   = tab
  currentPage.value = 1
  reports.value     = []
  fetchReports()
}

const goToPage = (page) => {
  currentPage.value = page
  fetchReports()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleResolve = async (report) => {
  if (!confirm(`Видалити цей ${report.content_type_name}?`)) return
  actionLoading.value[report.id] = true
  try {
    await moderationAPI.resolve(report.id, adminNotes.value[report.id] || '')
    reports.value = reports.value.filter(r => r.id !== report.id)
    pendingCount.value = Math.max(0, pendingCount.value - 1)
    toast.success('Контент видалено, скаргу закрито')
  } catch {
    toast.error('Помилка')
  } finally {
    actionLoading.value[report.id] = false
  }
}

const handleReject = async (report) => {
  actionLoading.value[report.id] = true
  try {
    await moderationAPI.reject(report.id, adminNotes.value[report.id] || '')
    reports.value = reports.value.filter(r => r.id !== report.id)
    pendingCount.value = Math.max(0, pendingCount.value - 1)
    toast.success('Скаргу відхилено')
  } catch {
    toast.error('Помилка')
  } finally {
    actionLoading.value[report.id] = false
  }
}

const contentLink = (report) => {
  if (report.content_type_name === 'post') {
    return `/posts/${report.object_slug}`
  }
  return `/posts/${report.object_post_slug}`
}

const formatDate = (str) => {
  try {
    return format(new Date(str), 'd MMM yyyy, HH:mm', { locale: uk })
  } catch { return str }
}
</script>