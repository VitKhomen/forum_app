<template>
  <div class="space-y-12">
    <!-- Trending Posts Slider -->
    <section v-if="!loadingTrending && trendingPosts.length">
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
      
      <PostsSlider 
        :posts="trendingPosts" 
        :autoplay="true" 
        :interval="5000"
        :key="trendingPosts.length"
      />
    </section>


    <!-- Recent Posts -->
    <section v-if="!loadingRecent && recentPosts.length">
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
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <PostCard
          v-for="post in recentPosts"
          :key="post.id"
          :post="post"
        />
      </div>
    </section>

    <!-- Loading State -->
    <div v-if="loadingTrending && loadingRecent" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Завантаження...</p>
    </div>

    <!-- Empty State -->
    <div v-if="!loadingTrending && !!loadingRecent && !trendingPosts.length && !popularPosts.length && !recentPosts.length" class="text-center py-12">
      <p class="text-gray-600 dark:text-gray-400 text-lg">Поки нічого нема</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { postsAPI } from '@/services/api'
import PostCard from '@/components/posts/PostCard.vue'
import PostsSlider from '@/components/posts/PostsSlider.vue'

const trendingPosts = ref([])
const recentPosts = ref([])

const loadingTrending = ref(true)
const loadingRecent = ref(true)

const fetchTrending = async () => {
  try {
    const { data } = await postsAPI.getTrending({ limit: 10, days: 14 })
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
  fetchRecent()
})
</script>