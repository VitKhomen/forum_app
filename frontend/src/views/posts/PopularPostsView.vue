<template>
  <div class="space-y-6">

    <!-- Заголовок + сортування + категорія -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Популярні</h1>

      <div class="flex flex-wrap items-center gap-3">
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

        <div class="flex bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-1 gap-1">
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

    <!-- Скелетон початкового завантаження — на місці постів -->
    <div v-if="loading && !items.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <SkeletonLoader v-for="i in 9" :key="`skeleton-initial-${i}`" type="post-card" />
    </div>

    <!-- Сітка постів -->
    <div v-else-if="items.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PostCard v-for="post in items" :key="post.id" :post="post" />
    </div>

    <!-- Empty -->
    <div v-else class="text-center py-20 text-gray-500 dark:text-gray-400">
      <p class="text-5xl mb-3">🔍</p>
      <p>Нічого не знайдено</p>
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
import { ref, watch, onMounted } from 'vue'
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
const activeSort       = ref('hot')

const sortTabs = [
  { value: 'hot',      icon: '🔥', label: 'Гарячі'    },
  { value: 'views',    icon: '👁',  label: 'Перегляди' },
  { value: 'likes',    icon: '❤️',  label: 'Лайки'     },
  { value: 'comments', icon: '💬',  label: 'Коментарі' },
]

const fetchPage = (params) => {
  const query = { ...params, page_size: 9, sort: activeSort.value }
  if (searchQuery.value.trim())  query.search         = searchQuery.value.trim()
  if (selectedCategory.value)    query.category__slug = selectedCategory.value
  return postsAPI.getPopular(query)
}

const { items, loading, hasMore, triggerEl, reset } = useInfiniteScroll(fetchPage)

const applyFilters = () => {
  updateURL()
  reset()
}

const setSort = (sort) => {
  activeSort.value = sort
  updateURL()
  reset()
}

const clearSearch = () => {
  searchQuery.value = ''
  updateURL()
  reset()
}

const updateURL = () => {
  router.replace({
    query: {
      sort:           activeSort.value !== 'hot' ? activeSort.value : undefined,
      search:         searchQuery.value || undefined,
      category__slug: selectedCategory.value || undefined,
    }
  })
}

// Синхронізація з URL (наприклад якщо пошук прийшов з хедера)
watch(() => route.query, (q) => {
  searchQuery.value      = q.search          || ''
  selectedCategory.value = q.category__slug  || ''
  activeSort.value       = q.sort            || 'hot'
  reset()
}, { immediate: true })

onMounted(() => {
  categoriesAPI.getAll().then(({ data }) => {
    categories.value = data.results || data
  })
})
</script>