<template>
  <div class="space-y-6">

    <!-- Header + Sort Tabs -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Популярні</h1>

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

    <!-- Search + Category filters -->
    <div class="flex flex-wrap gap-3">
      <input
        v-model="searchQuery"
        @keyup.enter="applyFilters"
        type="search"
        placeholder="Пошук..."
        class="flex-1 min-w-[200px] px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
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
        @click="applyFilters"
        class="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Шукати
      </button>
    </div>

    <!-- Posts Grid -->
    <div v-if="items.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PostCard v-for="post in items" :key="post.id" :post="post" />
    </div>

    <!-- Empty -->
    <div v-else-if="!loading" class="text-center py-20 text-gray-500 dark:text-gray-400">
      <p class="text-5xl mb-3">🔍</p>
      <p>Нічого не знайдено</p>
    </div>

    <!-- Тригер для IntersectionObserver + скелетони -->
    <div ref="triggerEl" class="py-8">
      <!-- Показуємо скелетони тільки коли завантажуємо наступну сторінку -->
      <div v-if="loading && items.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <SkeletonLoader 
          v-for="i in 6" 
          :key="`skeleton-more-${i}`" 
          type="post-card" 
        />
      </div>

      <!-- Початкове завантаження (коли items ще порожній) -->
      <div v-else-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <SkeletonLoader 
          v-for="i in 9" 
          :key="`skeleton-initial-${i}`" 
          type="post-card" 
        />
      </div>

      <!-- Кінець списку -->
      <p v-else-if="!hasMore && items.length" class="text-sm text-gray-400 dark:text-gray-500 text-center">
        Це всі пости 🎉
      </p>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsAPI, categoriesAPI } from '@/services/api'
import PostCard from '@/components/posts/PostCard.vue'
import { useInfiniteScroll } from '@/composables/useInfiniteScroll'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'

const route = useRoute()
const router = useRouter()

const categories = ref([])
const searchQuery = ref('')
const selectedCategory = ref('')
const activeSort = ref('hot')

const sortTabs = [
  { value: 'hot',      icon: '🔥', label: 'Гарячі'    },
  { value: 'views',    icon: '👁',  label: 'Перегляди' },
  { value: 'likes',    icon: '❤️',  label: 'Лайки'     },
  { value: 'comments', icon: '💬',  label: 'Коментарі' },
]

const fetchPage = (params) => {
  const query = { ...params, limit: 9, sort: activeSort.value }
  if (searchQuery.value.trim()) query.search = searchQuery.value.trim()
  if (selectedCategory.value)   query.category__slug = selectedCategory.value
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

const updateURL = () => {
  router.replace({
    query: {
      sort: activeSort.value !== 'hot' ? activeSort.value : undefined,
      search: searchQuery.value || undefined,
      category__slug: selectedCategory.value || undefined,
    }
  })
}

onMounted(() => {
  activeSort.value = route.query.sort || 'hot'
  searchQuery.value = route.query.search || ''
  selectedCategory.value = route.query.category__slug || ''

  categoriesAPI.getAll().then(({ data }) => {
    categories.value = data.results || data
  })
})
</script>