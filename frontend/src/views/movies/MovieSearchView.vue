<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          🎬 Пошук фільмів
        </h1>
        <p v-if="query && !loading" class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          За запитом "{{ query }}" знайдено {{ totalResults.toLocaleString() }} результатів
        </p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-gray-200 border-t-blue-500"></div>
    </div>

    <!-- Результати -->
    <div v-else-if="movies.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
      <RouterLink
        v-for="movie in movies"
        :key="movie.id"
        :to="`/movies/${movie.id}`"
        class="group"
      >
        <!-- Постер -->
        <div class="aspect-[2/3] rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-700 shadow-md group-hover:shadow-xl transition-shadow duration-300 mb-3">
          <img
            v-if="movie.poster_path"
            :src="`https://image.tmdb.org/t/p/w342${movie.poster_path}`"
            :alt="movie.title"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-5xl">🎬</div>
        </div>

        <!-- Назва та рейтинг -->
        <h3 class="text-sm font-medium text-gray-900 dark:text-white line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors leading-snug">
          {{ movie.title }}
        </h3>
        <div class="flex items-center gap-2 mt-1 text-xs text-gray-500 dark:text-gray-400">
          <span v-if="movie.release_date">{{ movie.release_date.slice(0, 4) }}</span>
          <span v-if="movie.vote_average" class="text-yellow-500 font-medium">⭐ {{ movie.vote_average.toFixed(1) }}</span>
        </div>
      </RouterLink>
    </div>

    <!-- Немає результатів -->
    <div v-else-if="query && !loading" class="text-center py-20 text-gray-500 dark:text-gray-400">
      <p class="text-5xl mb-4">🔍</p>
      <p class="text-lg">Нічого не знайдено за запитом "{{ query }}"</p>
      <p class="text-sm mt-2">Спробуйте інший запит або перевірте написання</p>
    </div>

    <!-- Початковий стан -->
    <div v-else-if="!query && !loading" class="text-center py-20 text-gray-500 dark:text-gray-400">
      <p class="text-5xl mb-4">🎬</p>
      <p>Введіть назву фільму у полі пошуку вгорі</p>
    </div>

    <!-- Пагінація -->
    <div v-if="totalPages > 1 && !loading" class="flex justify-center gap-2 flex-wrap">
      <button
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
        class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-40 transition"
      >
        ← Попередня
      </button>

      <template v-for="page in visiblePages" :key="page">
        <span v-if="page === '...'" class="px-3 py-2 text-gray-400">…</span>
        <button
          v-else
          @click="goToPage(page)"
          class="px-4 py-2 rounded-lg transition font-medium"
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
        class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-40 transition"
      >
        Наступна →
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { moviesAPI } from '@/services/api'

const route = useRoute()
const router = useRouter()

const movies = ref([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(0)
const totalResults = ref(0)

const query = computed(() => route.query.q || '')

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const pages = []
  if (total <= 7) {
    for (let i = 1; i <= total; i++) pages.push(i)
  } else {
    pages.push(1)
    if (current > 3) pages.push('...')
    for (let i = Math.max(2, current - 1); i <= Math.min(total - 1, current + 1); i++) pages.push(i)
    if (current < total - 2) pages.push('...')
    pages.push(total)
  }
  return pages
})

const search = async () => {
  if (!query.value) {
    movies.value = []
    return
  }
  loading.value = true
  try {
    const { data } = await moviesAPI.search(query.value, currentPage.value)
    movies.value = data.results || []
    totalResults.value = data.total_results || 0
    totalPages.value = Math.min(data.total_pages || 1, 20) // TMDB дає макс 500 стор
  } catch (e) {
    movies.value = []
  } finally {
    loading.value = false
  }
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  router.replace({ query: { ...route.query, page: page > 1 ? page : undefined } })
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(query, () => {
  currentPage.value = 1
  search()
})

watch(() => route.query.page, (p) => {
  currentPage.value = Number(p) || 1
  search()
})

onMounted(() => {
  currentPage.value = Number(route.query.page) || 1
  search()
})
</script>