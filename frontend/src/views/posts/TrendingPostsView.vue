<template>
  <div class="space-y-6">
    <!-- Page Title -->
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
        В тренді
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
        @click="applyFilters"
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
      <p class="text-gray-600 dark:text-gray-400">Трендові новини не знайдено</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center gap-2 flex-wrap">
      <button
        v-for="page in totalPages"
        :key="page"
        @click="changePage(page)"
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
const totalCount = ref(0)

const fetchPosts = async () => {
  try {
    loading.value = true
    const params = {
      page: currentPage.value,
      days: 14
    }
    
    const { data } = await postsAPI.getTrending(params)
    
    // Якщо бекенд повертає пагіновані дані
    if (data.results) {
      let filteredPosts = data.results
      
      // Фільтруємо по пошуку
      if (searchQuery.value.trim()) {
        const query = searchQuery.value.toLowerCase()
        filteredPosts = filteredPosts.filter(post => 
          post.title?.toLowerCase().includes(query) ||
          post.excerpt?.toLowerCase().includes(query)
        )
      }
      
      // Фільтруємо по категорії
      if (selectedCategory.value) {
        filteredPosts = filteredPosts.filter(post => 
          post.category?.slug === selectedCategory.value
        )
      }
      
      posts.value = filteredPosts
      totalCount.value = data.count
      
      // Якщо є фільтри, перераховуємо кількість сторінок
      if (searchQuery.value.trim() || selectedCategory.value) {
        totalPages.value = Math.ceil(filteredPosts.length / (data.results.length || 1))
      } else {
        totalPages.value = Math.ceil(data.count / (data.results.length || 20))
      }
    } else {
      // Якщо бекенд повертає простий масив
      posts.value = data
      totalPages.value = 1
    }
  } catch (error) {
    console.error('Error fetching trending posts:', error)
    posts.value = []
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
  fetchPosts()
}

const changePage = (page) => {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Читаємо параметри з URL при завантаженні
const syncFromRoute = () => {
  searchQuery.value = route.query.search || ''
  selectedCategory.value = route.query.category__slug || ''
}

// Оновлюємо пости при зміні сторінки
watch(currentPage, () => {
  fetchPosts()
})

// Оновлюємо пости при зміні query параметрів в URL
watch(() => route.query, () => {
  syncFromRoute()
  currentPage.value = 1
  fetchPosts()
}, { deep: true })

onMounted(() => {
  syncFromRoute()
  fetchCategories()
  fetchPosts()
})
</script>