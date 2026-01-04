<template>
  <div v-if="!loading && post" class="max-w-4xl mx-auto">
    <article class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <!-- Image -->
      <div v-if="post.image" class="aspect-video overflow-hidden">
        <img :src="post.image" :alt="post.title" class="w-full h-full object-cover" />
      </div>

      <!-- Content -->
      <div class="p-6 md:p-8">
        <!-- Category & Date -->
        <div class="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400 mb-4">
          <RouterLink
            v-if="post.category_info"
            :to="`/categories/${post.category_info.slug}`"
            class="text-blue-600 dark:text-blue-400 hover:underline font-medium"
          >
            {{ post.category_info.name }}
          </RouterLink>
          <span>•</span>
          <time>{{ formatDate(post.published_at || post.created_at) }}</time>
        </div>

        <!-- Title -->
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-6">
          {{ post.title }}
        </h1>

        <!-- Author & Stats -->
        <div class="flex items-center justify-between pb-6 mb-6 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
              <UserCircleIcon class="w-8 h-8 text-gray-500" />
            </div>
            <div>
              <p class="font-medium text-gray-900 dark:text-white">
                {{ post.author_info?.username }}
              </p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ post.author_info?.fullname }}
              </p>
            </div>
          </div>

          <div class="flex items-center gap-4 text-gray-500 dark:text-gray-400">
            <div class="flex items-center gap-1">
              <EyeIcon class="w-5 h-5" />
              <span>{{ post.views_count }}</span>
            </div>
            <div class="flex items-center gap-1">
              <ChatBubbleLeftIcon class="w-5 h-5" />
              <span>{{ post.comments_count || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="prose dark:prose-invert max-w-none mb-8">
          <div v-html="post.content" class="whitespace-pre-line"></div>
        </div>

        <!-- Additional Images -->
        <div v-if="post.images && post.images.length" class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
          <img
            v-for="img in post.images"
            :key="img.id"
            :src="img.image"
            alt="Post image"
            class="w-full h-48 object-cover rounded-lg"
          />
        </div>

        <!-- Tags -->
        <div v-if="post.tags && post.tags.length" class="flex flex-wrap gap-2 mb-8">
          <RouterLink
            v-for="tag in post.tags"
            :key="tag"
            :to="`/posts?tag=${tag}`"
            class="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-1 rounded-lg text-sm hover:bg-gray-200 dark:hover:bg-gray-600"
          >
            #{{ tag }}
          </RouterLink>
        </div>
      </div>
    </article>

    <!-- Comments Section -->
    <div class="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        Коментарі ({{ post.comments_count || 0 }})
      </h2>
      <p class="text-gray-600 dark:text-gray-400">Коментарі будуть доступні незабаром...</p>
    </div>
  </div>

  <!-- Loading -->
  <div v-else-if="loading" class="text-center py-12">
    <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
  </div>

  <!-- Not Found -->
  <div v-else class="text-center py-12">
    <p class="text-gray-600 dark:text-gray-400">Пост не знайдено</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { postsAPI } from '@/services/api'
import { UserCircleIcon, EyeIcon, ChatBubbleLeftIcon } from '@heroicons/vue/24/outline'
import { format } from 'date-fns'
import { uk } from 'date-fns/locale'

const route = useRoute()
const post = ref(null)
const loading = ref(true)

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    return format(new Date(dateString), 'd MMMM yyyy, HH:mm', { locale: uk })
  } catch {
    return dateString
  }
}

const fetchPost = async () => {
  try {
    loading.value = true
    const { data } = await postsAPI.getBySlug(route.params.slug)
    post.value = data
  } catch (error) {
    console.error('Error fetching post:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPost()
})
</script>