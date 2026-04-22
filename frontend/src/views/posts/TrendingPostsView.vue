<template>
  <div class="space-y-6">

    <!-- Заголовок + категорія -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">В тренді</h1>

      <div class="flex items-center gap-3">
        <select
          v-model="selectedCategory"
          @change="applyFilters"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                 bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm
                 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Всі категорії</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.slug">
            {{ cat.name }}
          </option>
        </select>
      </div>
    </div>

    <!-- Бейдж пошуку з хедера -->
    <div v-if="searchQuery" class="flex items-center gap-2">
      <span class="text-sm text-gray-500 dark:text-gray-400">Пошук:</span>
      <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-100 dark:bg-blue-900/30
                   text-blue-800 dark:text-blue-300 rounded-full text-sm">
        🔍 "{{ searchQuery }}"
        <button @click="clearSearch" class="hover:text-blue-600 ml-1">✕</button>
      </span>
    </div>

    <!-- Скелетон — на місці постів -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <SkeletonLoader v-for="i in 9" :key="`skeleton-${i}`" type="post-card" />
    </div>

    <!-- Сітка постів -->
    <div v-else-if="posts.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>

    <!-- Empty -->
    <div v-else class="text-center py-12 text-gray-600 dark:text-gray-400">
      <p class="text-5xl mb-3">🔥</p>
      <p>Трендових постів не знайдено</p>
    </div>

  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsAPI, categoriesAPI } from '@/services/api'
import PostCard from '@/components/posts/PostCard.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'

const route  = useRoute()
const router = useRouter()

const categories       = ref([])
const posts            = ref([])
const loading          = ref(false)
const searchQuery      = ref('')
const selectedCategory = ref('')

const fetchPosts = async () => {
  loading.value = true
  try {
    const params = { days: 180, limit: 30 }
    if (searchQuery.value.trim())  params.search         = searchQuery.value.trim()
    if (selectedCategory.value)    params.category__slug = selectedCategory.value

    const { data } = await postsAPI.getTrending(params)
    posts.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    console.error(e)
    posts.value = []
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  updateURL()
  fetchPosts()
}

const clearSearch = () => {
  searchQuery.value = ''
  updateURL()
  fetchPosts()
}

const updateURL = () => {
  router.replace({
    query: {
      search:         searchQuery.value      || undefined,
      category__slug: selectedCategory.value || undefined,
    }
  })
}

watch(() => route.query, (q) => {
  searchQuery.value      = q.search         || ''
  selectedCategory.value = q.category__slug || ''
  fetchPosts()
}, { immediate: true })

onMounted(() => {
  categoriesAPI.getAll().then(({ data }) => {
    categories.value = data.results || data
  })
})
</script>