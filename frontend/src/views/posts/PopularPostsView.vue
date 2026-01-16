<template>
  <div class="space-y-8">
    <!-- Page Title + Filters -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Всі пости
      </h1>

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
          @click="fetchPosts"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition whitespace-nowrap"
        >
          Застосувати
        </button>
      </div>
    </div>

    <!-- Posts Grid -->
    <div v-if="!loading && posts.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && !posts.length" class="text-center py-12 text-gray-600 dark:text-gray-400">
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
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 9  // має співпадати з backend (CommentPagination.page_size)
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

    const { data } = await postsAPI.getPopular(params)

    posts.value = data.results || []
    totalPages.value = data.count ? Math.ceil(data.count / pageSize) : 1

    // Оновлюємо URL
    router.push({
      query: {
        ...route.query,
        page: currentPage.value.toString(),
        search: searchQuery.value || undefined,
        category__slug: selectedCategory.value || undefined
      }
    })

    readyToRenderPages.value = true  // показуємо кнопки після завантаження
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

// Розумна генерація номерів сторінок (не показуємо всі 100)
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
watch(currentPage, (newPage) => {
  // Оновлюємо URL
  router.push({
    query: {
      ...route.query,
      page: newPage,
      search: searchQuery.value || undefined,
      category__slug: selectedCategory.value || undefined
    }
  })
  
  // Завантажуємо нові пости
  fetchPosts()
  
  // Скрол до верху
  window.scrollTo({ top: 0, behavior: 'smooth' })
}, { immediate: false })

watch(() => route.query, (query) => {
  const newPage = Number(query.page) || 1
  if (currentPage.value !== newPage) {
    currentPage.value = newPage
  }
  searchQuery.value = query.search || ''
  selectedCategory.value = query.category__slug || ''
}, { immediate: true, deep: true })

onMounted(() => {
  fetchCategories()
  fetchPosts()
})
</script>