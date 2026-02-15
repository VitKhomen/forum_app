<template>
  <div class="space-y-8">
    <!-- Заголовок сторінки -->
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white">
      Всі пости
    </h1>

    <!-- Активний тег (якщо фільтруємо за тегом з URL) -->
    <div
      v-if="selectedTag"
      class="flex items-center gap-3 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg"
    >
      <span class="text-sm text-gray-700 dark:text-gray-300">
        Фільтр за тегом:
      </span>
      <span class="px-3 py-1 bg-blue-600 text-white rounded-full text-sm font-medium">
        #{{ selectedTag }}
      </span>
      <button
        @click="clearTagFilter"
        class="ml-auto text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-xl leading-none"
      >
        ✕
      </button>
    </div>

    <!-- Список постів -->
    <div v-if="!loading && posts.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>

    <!-- Нічого не знайдено -->
    <div v-else-if="!loading && !posts.length" class="text-center py-16 text-gray-500 dark:text-gray-400">
      <svg class="mx-auto h-16 w-16 text-gray-400 mb-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      Нічого не знайдено
    </div>

    <!-- Завантаження -->
    <div v-if="loading" class="text-center py-16">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
    </div>

    <!-- Пагінація -->
    <div v-if="readyToRenderPages && totalPages > 1 && !loading" class="flex flex-wrap justify-center gap-2 mt-10">
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
const selectedTag = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = 9
const readyToRenderPages = ref(false)
const isUpdatingFromUrl = ref(false)

const fetchPosts = async () => {
  loading.value = true
  readyToRenderPages.value = false

  try {
    let data

    if (selectedTag.value) {
      const res = await postsAPI.getByTag(selectedTag.value, {
        page: currentPage.value,
        page_size: pageSize
      })
      data = res.data
    } else {
      const params = {
        page: currentPage.value,
        page_size: pageSize
      }
      const res = await postsAPI.getAll(params)
      data = res.data
    }

    posts.value = data.results || data || []
    totalPages.value = data.count ? Math.ceil(data.count / pageSize) : 1
    readyToRenderPages.value = true
  } catch (error) {
    console.error('Помилка завантаження постів:', error)
    posts.value = []
  } finally {
    loading.value = false
  }
}

const clearTagFilter = () => {
  selectedTag.value = ''
  currentPage.value = 1
  router.push({ path: '/posts' })
}

const changePage = (page) => {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

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

watch(
  () => route.query,
  (query) => {
    isUpdatingFromUrl.value = true

    currentPage.value = Number(query.page) || 1
    selectedTag.value = query.tag || ''

    fetchPosts()

    setTimeout(() => {
      isUpdatingFromUrl.value = false
    }, 50)
  },
  { immediate: true }
)

watch(currentPage, (newPage, oldPage) => {
  if (newPage !== oldPage && !isUpdatingFromUrl.value) {
    const query = {}
    if (newPage > 1) query.page = newPage.toString()
    if (selectedTag.value) query.tag = selectedTag.value
    router.push({ query })
  }
})

onMounted(() => {
  fetchPosts()
})
</script>