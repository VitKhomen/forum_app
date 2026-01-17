<template>
  <div class="space-y-8">
    <!-- Page Title + Filters -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          Всі пости
        </h1>
        <!-- Показуємо активні фільтри -->
        <div v-if="activeFiltersText" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {{ activeFiltersText }}
        </div>
      </div>

      <div class="flex flex-wrap gap-4 w-full md:w-auto">
        <input
          v-model="searchQuery"
          type="search"
          placeholder="Пошук..."
          class="flex-1 min-w-[200px] px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <select
          v-model="selectedCategory"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Всі категорії</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.slug">
            {{ cat.name }}
          </option>
        </select>

        <button
          @click="applyFilters"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition whitespace-nowrap"
        >
          Застосувати
        </button>

        <!-- Кнопка очистити фільтри -->
        <button
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition"
        >
          Очистити
        </button>
      </div>
    </div>

    <!-- Active Tag Filter -->
    <div v-if="selectedTag" class="flex items-center gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
      <span class="text-sm text-gray-700 dark:text-gray-300">
        Фільтр за тегом:
      </span>
      <span class="px-3 py-1 bg-blue-600 text-white rounded-full text-sm font-medium">
        #{{ selectedTag }}
      </span>
      <button
        @click="clearTagFilter"
        class="ml-auto text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
      >
        ✕
      </button>
    </div>

    <!-- Posts Grid -->
    <div v-if="!loading && posts.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && !posts.length" class="text-center py-12 text-gray-600 dark:text-gray-400">
      <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      Новини не знайдено
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
    </div>

    <!-- Pagination -->
    <div v-if="readyToRenderPages && totalPages > 1 && !loading" class="flex flex-wrap justify-center gap-2 mt-8">
      <!-- Попередня -->
      <button
        :disabled="currentPage === 1"
        @click="currentPage = currentPage - 1"
        class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 transition"
      >
        Попередня
      </button>

      <!-- Сторінки -->
      <button
        v-for="page in displayedPages"
        :key="page"
        @click="currentPage = page"
        :class="[
          'px-4 py-2 rounded-lg transition',
          currentPage === page
            ? 'bg-blue-600 text-white font-bold'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
        ]"
      >
        {{ page }}
      </button>

      <!-- Наступна -->
      <button
        :disabled="currentPage === totalPages"
        @click="currentPage = currentPage + 1"
        class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 transition"
      >
        Наступна
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsAPI, categoriesAPI } from '@/services/api'
import PostCard from '@/components/posts/PostCard.vue'

const route = useRoute()
const router = useRouter()

const posts = ref([])
const categories = ref([])
const loading = ref(true)
const searchQuery = ref('')
const selectedCategory = ref('')
const selectedTag = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 9
const readyToRenderPages = ref(false)

const fetchPosts = async () => {
  loading.value = true
  readyToRenderPages.value = false
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize
    }

    if (searchQuery.value.trim()) params.search = searchQuery.value.trim()
    if (selectedCategory.value) params.category__slug = selectedCategory.value
    if (selectedTag.value) params.tag = selectedTag.value

    const { data } = await postsAPI.getAll(params)

    posts.value = data.results || []
    totalPages.value = data.count ? Math.ceil(data.count / pageSize) : 1

    readyToRenderPages.value = true
  } catch (error) {
    console.error('Error fetching posts:', error)
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const { data } = await categoriesAPI.getAll()
    categories.value = data.results || data
  } catch (error) {
    console.error('Error fetching categories:', error)
  }
}

const applyFilters = () => {
  currentPage.value = 1
  updateURL()
  fetchPosts()
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedTag.value = ''
  currentPage.value = 1
  router.push({ path: '/posts' })
  fetchPosts()
}

const clearTagFilter = () => {
  selectedTag.value = ''
  currentPage.value = 1
  updateURL()
  fetchPosts()
}

const updateURL = () => {
  const query = {}
  if (currentPage.value > 1) query.page = currentPage.value.toString()
  if (searchQuery.value) query.search = searchQuery.value
  if (selectedCategory.value) query.category__slug = selectedCategory.value
  if (selectedTag.value) query.tag = selectedTag.value

  router.push({ query })
}

// Текст активних фільтрів
const activeFiltersText = computed(() => {
  const filters = []
  if (searchQuery.value) filters.push(`Пошук: "${searchQuery.value}"`)
  if (selectedCategory.value) {
    const cat = categories.value.find(c => c.slug === selectedCategory.value)
    if (cat) filters.push(`Категорія: ${cat.name}`)
  }
  if (selectedTag.value) filters.push(`Тег: #${selectedTag.value}`)
  return filters.length ? filters.join(' · ') : ''
})

// Чи є активні фільтри
const hasActiveFilters = computed(() => {
  return searchQuery.value || selectedCategory.value || selectedTag.value
})

// Розумна генерація номерів сторінок
const displayedPages = computed(() => {
  const pages = []
  const maxVisible = 7
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)

  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }

  return pages
})

// Синхронізація з URL
watch(currentPage, () => {
  updateURL()
  fetchPosts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
})

// Синхронізація з query параметрами
watch(() => route.query, (query) => {
  currentPage.value = Number(query.page) || 1
  searchQuery.value = query.search || ''
  selectedCategory.value = query.category__slug || ''
  selectedTag.value = query.tag || ''
  
  // Завантажуємо пости тільки якщо це перший раз
  if (!readyToRenderPages.value) {
    fetchPosts()
  }
}, { immediate: true, deep: true })

onMounted(() => {
  fetchCategories()
})
</script>