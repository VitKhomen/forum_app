<template>
  <div class="space-y-8">

    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ authorUsername ? `Пости @${authorUsername}` : 'Всі пости' }}
        </h1>
        <div v-if="activeFiltersText" class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {{ activeFiltersText }}
        </div>
      </div>

      <div class="flex flex-wrap gap-3 w-full md:w-auto">
        <select
          v-model="selectedCategory"
          @change="applyFilters"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Всі категорії</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.slug">
            {{ cat.name }}
          </option>
        </select>

        <button
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition"
        >
          Очистити фільтри
        </button>
      </div>
    </div>

    <!-- Бейджі фільтрів -->
    <div v-if="searchQuery || selectedTag" class="flex flex-wrap items-center gap-2">
      <span class="text-sm text-gray-500 dark:text-gray-400">Фільтри:</span>
      <span
        v-if="searchQuery"
        class="inline-flex items-center gap-1.5 px-3 py-1 bg-blue-100 dark:bg-blue-900/30
               text-blue-800 dark:text-blue-300 rounded-full text-sm"
      >
        🔍 "{{ searchQuery }}"
        <button @click="clearSearch" class="hover:text-blue-600 ml-1">✕</button>
      </span>
      <span
        v-if="selectedTag"
        class="inline-flex items-center gap-1.5 px-3 py-1 bg-green-100 dark:bg-green-900/30
               text-green-800 dark:text-green-300 rounded-full text-sm"
      >
        #{{ selectedTag }}
        <button @click="clearTagFilter" class="hover:text-green-600 ml-1">✕</button>
      </span>
    </div>

    <!-- Скелетон початкового завантаження — на місці постів -->
    <div v-if="loading && !items.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <SkeletonLoader v-for="i in 9" :key="`skeleton-initial-${i}`" type="post-card" />
    </div>

    <!-- Сітка постів -->
    <div v-else-if="items.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PostCard v-for="post in items" :key="post.id" :post="post" />
    </div>

    <!-- Empty -->
    <div v-else class="text-center py-12 text-gray-600 dark:text-gray-400">
      <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      Нічого не знайдено
    </div>

    <!-- Тригер — тільки для підвантаження наступних сторінок -->
    <div ref="triggerEl" class="py-4">
      <div v-if="loading && items.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <SkeletonLoader v-for="i in 6" :key="`skeleton-more-${i}`" type="post-card" />
      </div>
      <p v-else-if="!hasMore && items.length" class="text-sm text-gray-400 dark:text-gray-500 text-center">
        Це всі пости 🎉
      </p>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsAPI, categoriesAPI } from '@/services/api'
import PostCard from '@/components/posts/PostCard.vue'
import { useInfiniteScroll } from '@/composables/useInfiniteScroll'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'

const route  = useRoute()
const router = useRouter()

const categories       = ref([])
const searchQuery      = ref('')
const selectedCategory = ref('')
const selectedTag      = ref('')
const authorUsername   = ref('')

const fetchPage = (params) => {
  if (selectedTag.value) {
    return postsAPI.getByTag(selectedTag.value, { ...params, page_size: 9 })
  }
  const query = { ...params, page_size: 9 }
  if (searchQuery.value.trim())  query.search          = searchQuery.value.trim()
  if (selectedCategory.value)    query.category__slug  = selectedCategory.value
  if (authorUsername.value)      query.author_username = authorUsername.value
  return postsAPI.getAll(query)
}

const { items, loading, hasMore, triggerEl, reset } = useInfiniteScroll(fetchPage)

const applyFilters = () => {
  updateURL()
  reset()
}

const clearFilters = () => {
  searchQuery.value      = ''
  selectedCategory.value = ''
  selectedTag.value      = ''
  authorUsername.value   = ''
  router.push({ path: '/posts' })
  reset()
}

// Очистити тільки пошуковий запит — повертаємось на сторінку без search
const clearSearch = () => {
  searchQuery.value = ''
  updateURL()
  reset()
}

const clearTagFilter = () => {
  selectedTag.value = ''
  updateURL()
  reset()
}

const updateURL = () => {
  const query = {}
  if (searchQuery.value)      query.search          = searchQuery.value
  if (selectedCategory.value) query.category__slug  = selectedCategory.value
  if (selectedTag.value)      query.tag             = selectedTag.value
  if (authorUsername.value)   query.author_username = authorUsername.value
  router.replace({ query })
}

const activeFiltersText = computed(() => {
  const filters = []
  if (selectedCategory.value) {
    const cat = categories.value.find(c => c.slug === selectedCategory.value)
    if (cat) filters.push(`Категорія: ${cat.name}`)
  }
  if (authorUsername.value) filters.push(`Автор: @${authorUsername.value}`)
  return filters.join(' · ')
})

const hasActiveFilters = computed(() =>
  !!(searchQuery.value || selectedCategory.value || selectedTag.value || authorUsername.value)
)

watch(() => route.query, (q) => {
  searchQuery.value      = q.search          || ''
  selectedCategory.value = q.category__slug  || ''
  selectedTag.value      = q.tag             || ''
  authorUsername.value   = q.author_username || ''
  reset()
}, { immediate: true })

onMounted(() => {
  categoriesAPI.getAll().then(({ data }) => {
    categories.value = data.results || data
  })
})
</script>