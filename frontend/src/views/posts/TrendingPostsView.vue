<template>
  <div class="space-y-8">

    <!-- Заголовок -->
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
      В тренді
    </h1>

    <!-- Список постів -->
    <div v-if="!loading && posts.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>

    <!-- Порожній стан -->
    <div v-else-if="!loading && !posts.length" class="text-center py-16 text-gray-600 dark:text-gray-400">
      <p class="text-xl">Трендові новини не знайдено</p>
    </div>

    <!-- Завантаження -->
    <div v-if="loading" class="text-center py-16">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
    </div>

    <!-- Пагінація (покращена версія) -->
    <div v-if="totalPages > 1 && !loading" class="flex justify-center gap-2 flex-wrap mt-8">
      <button
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
        class="px-5 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 transition min-w-[100px]"
      >
        Попередня
      </button>

      <button
        v-for="page in displayedPages"
        :key="page"
        @click="changePage(page)"
        :class="[
          'px-4 py-2 rounded-lg min-w-[48px] transition',
          currentPage === page
            ? 'bg-blue-600 text-white font-semibold'
            : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
        ]"
      >
        {{ page }}
      </button>

      <button
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
        class="px-5 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-50 transition min-w-[100px]"
      >
        Наступна
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { postsAPI } from '@/services/api'
import PostCard from '@/components/posts/PostCard.vue'

const route = useRoute()
const router = useRouter()

const posts = ref([])
const loading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const pageSize = 20  // або те значення, яке використовує твій бекенд

const fetchPosts = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize,
      days: 14  // період трендовості — залишено як є
    }

    const { data } = await postsAPI.getTrending(params)

    posts.value = data.results || data || []
    totalCount.value = data.count || posts.value.length
    totalPages.value = data.count ? Math.ceil(data.count / pageSize) : 1
  } catch (error) {
    console.error('Помилка завантаження трендових постів:', error)
    posts.value = []
  } finally {
    loading.value = false
  }
}

// Покращена пагінація (показує не всі сторінки одразу)
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

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

watch(
  () => route.query.page,
  (newPage) => {
    const pageNum = Number(newPage) || 1
    if (pageNum !== currentPage.value) {
      currentPage.value = pageNum
      fetchPosts()
    }
  },
  { immediate: true }
)

watch(currentPage, (newPage) => {
  const query = {}
  if (newPage > 1) query.page = String(newPage)
  router.replace({ query })
})

onMounted(() => {
  fetchPosts()
})
</script>