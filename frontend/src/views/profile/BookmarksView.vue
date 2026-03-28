<template>
  <div class="max-w-5xl mx-auto space-y-6">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
          <svg class="w-8 h-8 text-amber-500" viewBox="0 0 24 24" fill="currentColor">
            <path d="M5 4a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 20V4z"/>
          </svg>
          Закладки
        </h1>
        <p class="text-gray-500 dark:text-gray-400 mt-1 text-sm">
          {{ totalCount }} збережених постів
        </p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-gray-200 border-t-amber-500"></div>
    </div>

    <!-- Empty -->
    <div v-else-if="!bookmarks.length" class="text-center py-24">
      <svg class="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M5 4a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 20V4z"/>
      </svg>
      <p class="text-xl font-semibold text-gray-500 dark:text-gray-400">Поки немає закладок</p>
      <p class="text-sm text-gray-400 dark:text-gray-500 mt-2">
        Натискай 🔖 на постах щоб зберігати їх тут
      </p>
      <RouterLink
        to="/posts"
        class="mt-6 inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors"
      >
        Перейти до постів →
      </RouterLink>
    </div>

    <!-- Bookmarks Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div
        v-for="bookmark in bookmarks"
        :key="bookmark.id"
        class="relative group"
      >
        <!-- Картка поста -->
        <PostCard :post="bookmark.post_detail" />

        <!-- Кнопка видалити із закладок (появляється при hover) -->
        <button
          @click="removeBookmark(bookmark)"
          class="absolute top-3 right-3 p-1.5 rounded-lg bg-white/90 dark:bg-gray-800/90 text-amber-500 shadow-md opacity-0 group-hover:opacity-100 transition-all hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-500"
          title="Видалити із закладок"
        >
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M5 4a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 20V4z"/>
          </svg>
        </button>

        <!-- Дата збереження -->
        <p class="text-xs text-gray-400 dark:text-gray-500 mt-2 text-right px-1">
          Збережено {{ formatDate(bookmark.created_at) }}
        </p>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1 && !loading" class="flex justify-center gap-2 flex-wrap pt-4">
      <button
        :disabled="currentPage === 1"
        @click="goToPage(currentPage - 1)"
        class="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 disabled:opacity-40 transition"
      >
        ← Попередня
      </button>

      <button
        v-for="page in totalPages"
        :key="page"
        @click="goToPage(page)"
        class="px-4 py-2 rounded-lg transition font-medium"
        :class="currentPage === page
          ? 'bg-amber-500 text-white'
          : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'"
      >
        {{ page }}
      </button>

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
import { ref, computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { bookmarksAPI } from '@/services/api'
import { useToast } from 'vue-toastification'
import { formatDistanceToNow } from 'date-fns'
import { uk } from 'date-fns/locale'
import PostCard from '@/components/posts/PostCard.vue'

const toast = useToast()

const bookmarks = ref([])
const loading = ref(false)
const currentPage = ref(1)
const totalCount = ref(0)
const pageSize = 12

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize))

const fetchBookmarks = async () => {
  loading.value = true
  try {
    const { data } = await bookmarksAPI.getAll({ page: currentPage.value })
    bookmarks.value = data.results || []
    totalCount.value = data.count || 0
  } catch (error) {
    console.error(error)
    toast.error('Помилка завантаження закладок')
  } finally {
    loading.value = false
  }
}

const removeBookmark = async (bookmark) => {
  try {
    await bookmarksAPI.toggle(bookmark.post)
    bookmarks.value = bookmarks.value.filter(b => b.id !== bookmark.id)
    totalCount.value--
    toast.success('Видалено із закладок')
  } catch {
    toast.error('Помилка видалення')
  }
}

const goToPage = (page) => {
  currentPage.value = page
  fetchBookmarks()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const formatDate = (dateString) => {
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true, locale: uk })
  } catch {
    return ''
  }
}

onMounted(fetchBookmarks)
</script>