<template>
  <div class="space-y-12">
    <!-- Hero Section -->
    <section class="bg-gradient-to-r from-blue-600 to-blue-800 dark:from-blue-800 dark:to-blue-900 rounded-xl p-8 md:p-12 text-white">
      <div class="max-w-3xl">
        <h1 class="text-4xl md:text-5xl font-bold mb-4">
          Залишайтесь в курсі подій
        </h1>
        <p class="text-lg md:text-xl mb-6 text-blue-100">
          Читайте найактуальніші новини, статті та аналітику
        </p>
        <RouterLink
          to="/posts"
          class="inline-block bg-white text-blue-600 hover:bg-blue-50 px-6 py-3 rounded-lg font-semibold transition"
        >
          Переглянути новини
        </RouterLink>
      </div>
    </section>

    <!-- Trending Posts -->
    <section v-if="!loadingTrending && trendingPosts.length">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
          🔥 В тренді
        </h2>
        <RouterLink
          to="/posts?filter=trending"
          class="text-blue-600 dark:text-blue-400 hover:underline text-sm font-medium"
        >
          Дивитись все →
        </RouterLink>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <PostCard
          v-for="post in trendingPosts"
          :key="post.id"
          :post="post"
        />
      </div>
    </section>

    <!-- Popular Posts -->
    <section v-if="!loadingPopular && popularPosts.length">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
          ⭐ Популярні
        </h2>
        <RouterLink
          to="/posts?filter=popular"
          class="text-blue-600 dark:text-blue-400 hover:underline text-sm font-medium"
        >
          Дивитись все →
        </RouterLink>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <PostCard
          v-for="post in popularPosts"
          :key="post.id"
          :post="post"
        />
      </div>
    </section>

    <!-- Recent Posts -->
    <section v-if="!loadingRecent && recentPosts.length">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
          📰 Останні новини
        </h2>
        <RouterLink
          to="/posts"
          class="text-blue-600 dark:text-blue-400 hover:underline text-sm font-medium"
        >
          Дивитись все →
        </RouterLink>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <PostCard
          v-for="post in recentPosts"
          :key="post.id"
          :post="post"
        />
      </div>
    </section>

    <!-- Loading State -->
    <div v-if="loadingTrending && loadingPopular && loadingRecent" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Завантаження...</p>
    </div>

    <!-- Empty State -->
    <div v-if="!loadingTrending && !loadingPopular && !loadingRecent && !trendingPosts.length && !popularPosts.length && !recentPosts.length" class="text-center py-12">
      <p class="text-gray-600 dark:text-gray-400 text-lg">Поки що немає новин</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { postsAPI } from '@/services/api'
import PostCard from '@/components/posts/PostCard.vue'

const trendingPosts = ref([])
const popularPosts = ref([])
const recentPosts = ref([])

const loadingTrending = ref(true)
const loadingPopular = ref(true)
const loadingRecent = ref(true)

const fetchTrending = async () => {
  try {
    const { data } = await postsAPI.getTrending({ limit: 6, days: 7 })
    trendingPosts.value = data
  } catch (error) {
    // Якщо 401 - користувач не авторизований, просто не показуємо секцію
    if (error.response?.status === 401) {
      console.log('Trending posts require authentication')
    } else {
      console.error('Error fetching trending posts:', error)
    }
  } finally {
    loadingTrending.value = false
  }
}

const fetchPopular = async () => {
  try {
    const { data } = await postsAPI.getPopular({ limit: 6 })
    popularPosts.value = data
  } catch (error) {
    // Якщо 401 - користувач не авторизований, просто не показуємо секцію
    if (error.response?.status === 401) {
      console.log('Popular posts require authentication')
    } else {
      console.error('Error fetching popular posts:', error)
    }
  } finally {
    loadingPopular.value = false
  }
}

const fetchRecent = async () => {
  try {
    const { data } = await postsAPI.getAll({ page_size: 6 })
    recentPosts.value = data.results || data
  } catch (error) {
    console.error('Error fetching recent posts:', error)
  } finally {
    loadingRecent.value = false
  }
}

onMounted(() => {
  fetchTrending()
  fetchPopular()
  fetchRecent()
})
</script>