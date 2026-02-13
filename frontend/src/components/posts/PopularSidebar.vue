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
          :to="{ path: '/posts', query: { tag: tag.name } }"
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
      <div class="p-5 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <FireIcon class="w-5 h-5 text-orange-500" />
          Популярні Пости
        </h3>
      </div>

      <div v-if="posts && posts.length" class="divide-y divide-gray-100 dark:divide-gray-700/50">
        <article
          v-for="(post, index) in posts"
          :key="post.slug"
          class="group relative"
        >
          <RouterLink :to="`/posts/${post.slug}`" class="block">

            <!-- З зображенням — image card з overlay -->
            <div v-if="post.image" class="relative h-32 overflow-hidden">
              <!-- Зображення на весь блок -->
              <img
                :src="post.image"
                :alt="post.title"
                class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              />

              <!-- Градієнт знизу -->
              <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent" />


              <!-- Заголовок і мета знизу поверх картинки -->
              <div class="absolute bottom-0 left-0 right-0 p-3">
                <h4 class="text-sm font-semibold text-white line-clamp-2 leading-snug mb-1.5">
                  {{ post.title }}
                </h4>
                <div class="flex items-center gap-3 text-xs text-white/75">
                  <div class="flex items-center gap-2">
                    <AuthorWithKarma
                      size="sm"
                      :username="post.author_username"
                      :karma="post.author_karma_points || 0"
                      :level="post.author_karma_level || 1"
                    />
                  </div>
                  <div class="flex items-center gap-1">
                    <EyeIcon class="w-3.5 h-3.5" />
                    <span>{{ formatNumber(post.views_count || 0) }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <ChatBubbleLeftIcon class="w-3.5 h-3.5" />
                    <span>{{ commentsCount(post.id) }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <HeartIcon class="w-3.5 h-3.5" />
                    <span>{{ post.likes_count || 0 }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="relative h-24 overflow-hidden flex items-center gap-3 px-4"
              :class="gradientClass(index)"
              >
              
              <!-- Заголовок + мета -->
              <div class="flex-1 min-w-0">
                <h4 class="text-sm font-semibold text-white line-clamp-2 leading-snug mb-1">
                  {{ post.title }}
                </h4>
                <div class="flex items-center gap-3 text-xs text-white/70">
                  <div class="flex items-center gap-2">
                    <AuthorWithKarma
                      size="sm"
                      :username="post.author_username"
                      :karma="post.author_karma_points || 0"
                      :level="post.author_karma_level || 1"
                    />
                  </div>
                  <div class="flex items-center gap-1">
                    <EyeIcon class="w-3 h-3" />
                    <span>{{ formatNumber(post.views_count || 0) }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <ChatBubbleLeftIcon class="w-3 h-3" />
                    <span>{{ commentsCount(post.id) }}</span>
                  </div>
                  <div class="flex items-center gap-1">
                    <HeartIcon class="w-3 h-3" />
                    <span>{{ post.likes_count || 0 }}</span>
                  </div>
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
          class="block text-center text-orange-600 dark:text-orange-400 hover:text-orange-700 dark:hover:text-orange-300 font-medium text-sm transition"
        >
          Показати всі популярні →
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { TagIcon, FireIcon, EyeIcon, ChatBubbleLeftIcon, HeartIcon } from '@heroicons/vue/24/outline'
import { useCommentsSync } from '@/composables/useCommentsSync'
import AuthorWithKarma from '@/components/ui/KarmaBadge.vue'

const props = defineProps({
  tags: { type: Array, default: () => [] },
  posts: { type: Array, default: () => [] }
})

const { getCommentsCount, subscribe } = useCommentsSync()

const commentsCount = (postId) => {
  const cached = getCommentsCount(postId)
  if (cached !== undefined) return cached
  const post = props.posts.find(p => p.id === postId)
  return post ? (post.comments_count || 0) : 0
}

let unsubscribe = null
onMounted(() => { unsubscribe = subscribe(() => {}) })
onUnmounted(() => { if (unsubscribe) unsubscribe() })

// Різні градієнти для постів без зображення
const gradients = [
  'bg-gradient-to-r from-orange-500 to-red-500',
  'bg-gradient-to-r from-blue-500 to-indigo-600',
  'bg-gradient-to-r from-emerald-500 to-teal-600',
  'bg-gradient-to-r from-purple-500 to-pink-500',
  'bg-gradient-to-r from-amber-500 to-orange-600',
]

const gradientClass = (index) => gradients[index % gradients.length]

const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}
</script>