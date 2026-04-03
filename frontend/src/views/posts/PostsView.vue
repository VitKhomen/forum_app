<template>
  <div class="space-y-8">
    <!-- Заголовок + фільтри (без змін) -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ authorUsername ? `Пости @${authorUsername}` : 'Всі пости' }}
        </h1>
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
        <button
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition"
        >
          Очистити
        </button>
      </div>
    </div>

    <!-- Тег фільтр -->
    <div v-if="selectedTag" class="flex items-center gap-2 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
      <span class="text-sm text-gray-700 dark:text-gray-300">Фільтр за тегом:</span>
      <span class="px-3 py-1 bg-blue-600 text-white rounded-full text-sm font-medium">#{{ selectedTag }}</span>
      <button @click="clearTagFilter" class="ml-auto text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">✕</button>
    </div>

    <!-- Сітка постів -->
    <div v-if="items.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PostCard v-for="post in items" :key="post.id" :post="post" />
    </div>

    <!-- Empty (тільки якщо не завантажується і немає результатів) -->
    <div v-else-if="!loading" class="text-center py-12 text-gray-600 dark:text-gray-400">
      <svg class="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      Нічого не знайдено
    </div>

    <!-- Тригер для IntersectionObserver + спінер -->
    <div ref="triggerEl" class="py-8 flex justify-center">
      <div v-if="loading" class="animate-spin rounded-full h-10 w-10 border-4 border-gray-300 border-t-blue-600" />
      <p v-else-if="!hasMore && items.length" class="text-sm text-gray-400 dark:text-gray-500">
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

const route  = useRoute()
const router = useRouter()

const categories      = ref([])
const searchQuery     = ref('')
const selectedCategory = ref('')
const selectedTag     = ref('')
const authorUsername  = ref('')

// Функція що передається в composable — завжди бере актуальні фільтри
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

// Застосувати фільтри = скинути і почати з нуля
const applyFilters = () => {
  updateURL()
  reset()
}

const clearFilters = () => {
  searchQuery.value     = ''
  selectedCategory.value = ''
  selectedTag.value     = ''
  authorUsername.value  = ''
  router.push({ path: '/posts' })
  reset()
}

const clearTagFilter = () => {
  selectedTag.value = ''
  updateURL()
  reset()
}

const updateURL = () => {
  const query = {}
  if (searchQuery.value)      query.search         = searchQuery.value
  if (selectedCategory.value) query.category__slug = selectedCategory.value
  if (selectedTag.value)      query.tag            = selectedTag.value
  if (authorUsername.value)   query.author_username = authorUsername.value
  router.push({ query })
}

const activeFiltersText = computed(() => {
  const filters = []
  if (searchQuery.value)      filters.push(`Пошук: "${searchQuery.value}"`)
  if (selectedCategory.value) {
    const cat = categories.value.find(c => c.slug === selectedCategory.value)
    if (cat) filters.push(`Категорія: ${cat.name}`)
  }
  if (selectedTag.value)    filters.push(`Тег: #${selectedTag.value}`)
  if (authorUsername.value) filters.push(`Автор: @${authorUsername.value}`)
  return filters.join(' · ')
})

const hasActiveFilters = computed(() =>
  !!(searchQuery.value || selectedCategory.value || selectedTag.value || authorUsername.value)
)

// Синхронізація з URL при зміні query
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