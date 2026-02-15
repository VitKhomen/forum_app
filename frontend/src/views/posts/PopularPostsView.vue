<template>
  <div class="space-y-6">

    <!-- Заголовок + Сортування -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Популярні</h1>

      <!-- Сортування (таби) -->
      <div class="flex bg-gray-100 dark:bg-gray-800 rounded-xl p-1 gap-1">
        <button
          v-for="tab in sortTabs"
          :key="tab.value"
          @click="setSort(tab.value)"
          class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all"
          :class="activeSort === tab.value
            ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
            : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
        >
          <span>{{ tab.icon }}</span>
          <span class="hidden sm:inline">{{ tab.label }}</span>
        </button>
      </div>
    </div>

    <!-- Завантаження -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-gray-200 border-t-blue-500"></div>
    </div>

    <!-- Список постів -->
    <div v-else-if="posts.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>

    <!-- Порожньо -->
    <div v-else class="text-center py-20 text-gray-500 dark:text-gray-400">
      <p class="text-5xl mb-3">🔍</p>
      <p>Нічого не знайдено</p>
    </div>

    <!-- Пагінація -->
    <div v-if="totalPages > 1 && !loading" class="flex flex-wrap justify-center gap-2 mt-6">
      <button
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
        class="px-5 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 transition min-w-[100px]"
      >
        ← Попередня
      </button>

      <template v-for="page in visiblePages" :key="page">
        <span v-if="page === '...'" class="px-3 py-2 text-gray-400">…</span>
        <button
          v-else
          @click="goToPage(page)"
          class="px-4 py-2 rounded-lg transition font-medium min-w-[48px]"
          :class="currentPage === page
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'"
        >
          {{ page }}
        </button>
      </template>

      <button
        :disabled="currentPage === totalPages"
        @click="goToPage(currentPage + 1)"
        class="px-5 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 transition min-w-[100px]"
      >
        Наступна →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsAPI } from '@/services/api'
import PostCard from '@/components/posts/PostCard.vue'

const route = useRoute()
const router = useRouter()

const posts = ref([])
const loading = ref(true)
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 9
const activeSort = ref('hot')

const sortTabs = [
  { value: 'hot',      icon: '🔥', label: 'Гарячі'     },
  { value: 'views',    icon: '👁',  label: 'Перегляди'  },
  { value: 'likes',    icon: '❤️',  label: 'Лайки'      },
  { value: 'comments', icon: '💬',  label: 'Коментарі'  },
]

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize))

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const pages = []

  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
    return pages
  }

  pages.push(1)
  if (current > 3) pages.push('...')
  for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) {
    pages.push(i)
  }
  if (current < total - 2) pages.push('...')
  pages.push(total)
  return pages
})

const fetchPosts = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize,
      sort: activeSort.value,
    }

    const { data } = await postsAPI.getPopular(params)
    posts.value = data.results || []
    totalCount.value = data.count || 0

    // Синхронізація URL (тільки sort та page)
    router.replace({
      query: {
        sort: activeSort.value !== 'hot' ? activeSort.value : undefined,
        page: currentPage.value > 1 ? String(currentPage.value) : undefined,
      }
    })
  } catch (error) {
    console.error('Помилка завантаження популярних постів:', error)
  } finally {
    loading.value = false
  }
}

const setSort = (sort) => {
  activeSort.value = sort
  currentPage.value = 1
  fetchPosts()
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchPosts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  // Зчитуємо з URL тільки sort та page
  activeSort.value = route.query.sort || 'hot'
  currentPage.value = Number(route.query.page) || 1
  fetchPosts()
})
</script>