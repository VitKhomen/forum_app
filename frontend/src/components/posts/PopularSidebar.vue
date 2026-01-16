<template>
  <div class="space-y-6">
    <!-- Популярні Теги -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
        <TagIcon class="w-5 h-5" />
        Популярні Теги
      </h3>
      
      <div v-if="tags && tags.length" class="flex flex-wrap gap-2">
        <RouterLink
          v-for="tag in tags"
          :key="tag.name"
          :to="`/posts?tag=${tag.name}`"
          class="inline-block px-3 py-1.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm font-medium hover:bg-blue-200 dark:hover:bg-blue-800 transition"
        >
          #{{ tag.name }}
        </RouterLink>
      </div>
      
      <div v-else class="text-center text-gray-500 dark:text-gray-400 py-4">
        Немає тегів
      </div>
    </div>

    <!-- Популярні Пости -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <FireIcon class="w-5 h-5" />
          Популярні Пости
        </h3>
      </div>

      <div v-if="posts && posts.length" class="divide-y divide-gray-200 dark:divide-gray-700">
        <article
          v-for="(post, index) in posts"
          :key="post.slug"
          class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
        >
          <RouterLink :to="`/posts/${post.slug}`" class="flex gap-4">
            <!-- Номер або Зображення -->
            <div class="flex-shrink-0">
              <div v-if="post.image" class="w-20 h-20 rounded-lg overflow-hidden">
                <img
                  :src="post.image"
                  :alt="post.title"
                  class="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
                />
              </div>
              <div v-else class="w-20 h-20 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span class="text-2xl font-bold text-white">{{ index + 1 }}</span>
              </div>
            </div>

            <!-- Контент -->
            <div class="flex-1 min-w-0">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-1 line-clamp-2 hover:text-blue-600 dark:hover:text-blue-400 transition">
                {{ post.title }}
              </h4>
              
              <!-- Meta Info -->
              <div class="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                <div class="flex items-center gap-1">
                  <EyeIcon class="w-3.5 h-3.5" />
                  <span>{{ post.views_count || 0 }}</span>
                </div>
                <div class="flex items-center gap-1">
                  <ChatBubbleLeftIcon class="w-3.5 h-3.5" />
                  <span>{{ post.comments_count || 0 }}</span>
                </div>
              </div>
            </div>
          </RouterLink>
        </article>
      </div>

      <div v-else class="p-6 text-center text-gray-500 dark:text-gray-400">
        Немає постів для відображення
      </div>

      <!-- Кнопка "Показати всі" -->
      <div v-if="posts && posts.length" class="p-4 border-t border-gray-200 dark:border-gray-700">
        <RouterLink
          to="/posts/popular"
          class="block text-center text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium text-sm transition"
        >
          Показати всі популярні →
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { 
  TagIcon, 
  FireIcon, 
  EyeIcon, 
  ChatBubbleLeftIcon 
} from '@heroicons/vue/24/outline'

defineProps({
  tags: {
    type: Array,
    default: () => []
  },
  posts: {
    type: Array,
    default: () => []
  }
})
</script>