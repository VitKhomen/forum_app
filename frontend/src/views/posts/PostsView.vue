<template>
  <div class="space-y-6">
    <!-- Page Title -->
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        Всі новини
      </h1>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-4">
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
        class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Застосувати
      </button>
    </div>

    <!-- Posts Grid -->
    <div v-if="!loading && posts.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && !posts.length" class="text-center py-12">
      <p class="text-gray-600 dark:text-gray-400">Новини не знайдено</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center gap-2">
      <button
        v-for="page in totalPages"
        :key="page"
        @click="currentPage = page"
        :class="[
          'px-4 py-2 rounded-lg transition',
          currentPage === page
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
        ]"
      >
        {{ page }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { postsAPI, categoriesAPI } from '@/services/api'
import PostCard from '@/components/posts/PostCard.vue'

const route = useRoute()

const posts = ref([])
const categories = ref([])
const loading = ref(true)
const searchQuery = ref('')
const selectedCategory = ref('')
const currentPage = ref(1)
const totalPages = ref(1)

const fetchPosts = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
    }
    
    // Додаємо пошук тільки якщо є значення
    if (searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
    }
    
    // Додаємо категорію тільки якщо обрана
    if (selectedCategory.value) {
      params.category__slug = selectedCategory.value
    }
    
    const { data } = await postsAPI.getAll(params)
    posts.value = data.results || data
    totalPages.value = Math.ceil((data.count || posts.value.length) / 20)
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

// Читаємо параметри з URL при завантаженні
const syncFromRoute = () => {
  searchQuery.value = route.query.search || ''
  selectedCategory.value = route.query.category__slug || ''
}

// Оновлюємо пости при зміні сторінки
watch(currentPage, () => {
  fetchPosts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
})

// Оновлюємо пости при зміні query параметрів в URL
watch(() => route.query, () => {
  syncFromRoute()
  currentPage.value = 1 // скидаємо на першу сторінку
  fetchPosts()
}, { deep: true })

onMounted(() => {
  syncFromRoute() // читаємо параметри з URL
  fetchCategories()
  fetchPosts()
})
</script>