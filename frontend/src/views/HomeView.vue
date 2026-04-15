<template>
  <div class="space-y-12">
    <!-- Trending Posts Slider -->
    <section>
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
          В тренді
        </h2>
        <RouterLink
          to="/posts/trending"
          class="text-blue-600 dark:text-blue-400 hover:underline text-sm font-medium"
        >
          Дивитись все →
        </RouterLink>
      </div>

      <!-- Скелетон для слайдера -->
      <div v-if="loadingTrending" class="h-[420px] bg-gray-200 dark:bg-gray-700 rounded-2xl animate-pulse" />

      <!-- Реальний слайдер -->
      <PostsSlider 
        v-else-if="trendingPosts.length"
        :posts="trendingPosts" 
        :autoplay="true" 
        :interval="5000"
        :key="trendingPosts.length"
      />

      <!-- Якщо нічого не завантажилось -->
      <div v-else class="h-[420px] flex items-center justify-center bg-gray-100 dark:bg-gray-800 rounded-2xl">
        <p class="text-gray-500 dark:text-gray-400">Не вдалося завантажити тренди</p>
      </div>
    </section>

    <!-- Recent Posts -->
    <section>
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
          Останні пости
        </h2>
        <RouterLink
          to="/posts"
          class="text-blue-600 dark:text-blue-400 hover:underline text-sm font-medium"
        >
          Дивитись все →
        </RouterLink>
      </div>

      <!-- Скелетони для останніх постів -->
      <div v-if="loadingRecent" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <SkeletonLoader 
          v-for="i in 6" 
          :key="`recent-skeleton-${i}`" 
          type="post-card" 
        />
      </div>

      <!-- Реальні пости -->
      <div v-else-if="recentPosts.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <PostCard
          v-for="post in recentPosts"
          :key="post.id"
          :post="post"
        />
      </div>

      <!-- Якщо нічого немає -->
      <div v-else class="text-center py-12 bg-gray-50 dark:bg-gray-900 rounded-xl">
        <p class="text-gray-500 dark:text-gray-400">Поки немає останніх постів</p>
      </div>
    </section>

    <!-- Загальний спінер зверху (якщо хочеш залишити на самому початку завантаження) -->
    <!-- Можна видалити, бо тепер є окремі скелетони -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { postsAPI } from '@/services/api'
import PostCard from '@/components/posts/PostCard.vue'
import PostsSlider from '@/components/posts/PostsSlider.vue'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'

const trendingPosts = ref([])
const recentPosts = ref([])

const loadingTrending = ref(true)
const loadingRecent = ref(true)

const fetchTrending = async () => {
  try {
    const { data } = await postsAPI.getTrending({ limit: 12, days: 180 })
    trendingPosts.value = data
  } catch (error) {
    if (error.response?.status === 401) {
      console.log('Trending posts require authentication')
    } else {
      console.error('Error fetching trending posts:', error)
    }
  } finally {
    loadingTrending.value = false
  }
}


const fetchRecent = async () => {
  try {
    const { data } = await postsAPI.getAll({ limit: 6 })
    recentPosts.value = data.results || data
  } catch (error) {
    console.error('Error fetching recent posts:', error)
  } finally {
    loadingRecent.value = false
  }
}

onMounted(() => {
  fetchTrending()
  fetchRecent()
})
</script>