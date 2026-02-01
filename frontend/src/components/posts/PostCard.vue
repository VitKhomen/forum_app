<template>
  <article class="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-md hover:shadow-xl transition-shadow">
    <!-- Image -->
    <RouterLink :to="`/posts/${post.slug}`">
      <div class="aspect-video overflow-hidden bg-gray-200 dark:bg-gray-700">
        <img
          v-if="post.image"
          :src="post.image"
          :alt="post.title"
          class="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
        />
        <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
          <NewspaperIcon class="w-16 h-16" />
        </div>
      </div>
    </RouterLink>

    <!-- Content -->
    <div class="p-5">
      <!-- Category & Date -->
      <div class="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400 mb-2">
        <RouterLink
          v-if="post.category_name"
          :to="`/categories/${post.category}`"
          class="text-blue-600 dark:text-blue-400 hover:underline font-medium"
        >
          {{ post.category_name }}
        </RouterLink>
        <span>•</span>
        <time>{{ formatDate(post.published_at || post.created_at) }}</time>
      </div>

      <!-- Title -->
      <RouterLink :to="`/posts/${post.slug}`">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2 hover:text-blue-600 dark:hover:text-blue-400 transition">
          {{ post.title }}
        </h3>
      </RouterLink>

      <!-- Excerpt -->
      <p class="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-3">
        {{ post.excerpt || truncateText(post.content, 120) }}
      </p>

      <!-- Footer -->
      <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <!-- Author -->
        <div class="flex items-center gap-2">
          <UserCircleIcon class="w-5 h-5" />
          <span>{{ post.author_username }}</span>
        </div>

        <!-- Stats -->
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1" :title="'Переглядів: ' + post.views_count">
            <EyeIcon class="w-4 h-4" />
            <span>{{ post.views_count || 0 }}</span>
          </div>
          <div class="flex items-center gap-1" :title="'Коментарів: ' + localCommentsCount">
            <ChatBubbleLeftIcon class="w-4 h-4" />
            <!-- ✅ ЗМІНЕНО: Використовуємо локальну змінну -->
            <span>{{ localCommentsCount }}</span>
          </div>

          <!-- Like Button -->
          <LikeButton
            content-type="post"
            :object-id="post.id"
            :initial-likes-count="post.likes_count || 0"
            :initial-is-liked="post.is_liked || false"
          />
        </div>
      </div>

      <!-- Tags -->
      <div v-if="post.tags && post.tags.length" class="mt-3 flex flex-wrap gap-2">
        <RouterLink
          v-for="tag in post.tags.slice(0, 3)"
          :key="tag"
          :to="`/posts?tag=${tag}`"
          class="text-xs bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-2 py-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600"
        >
          #{{ tag }}
        </RouterLink>
      </div>
    </div>
  </article>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { 
  NewspaperIcon, 
  UserCircleIcon, 
  EyeIcon, 
  ChatBubbleLeftIcon 
} from '@heroicons/vue/24/outline'
import { format } from 'date-fns'
import { uk } from 'date-fns/locale'
import LikeButton from '@/components/ui/LikeButton.vue'
import { useCommentsSync } from '@/composables/useCommentsSync'

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const { subscribe, getCommentsCount } = useCommentsSync()

// ✅ ДОДАНО: Локальна змінна для відстеження коментарів
const localCommentsCount = ref(props.post.comments_count || 0)

// ✅ ДОДАНО: Watch для синхронізації з props (якщо post оновиться ззовні)
watch(() => props.post.comments_count, (newCount) => {
  if (newCount !== undefined && newCount !== null) {
    localCommentsCount.value = newCount
  }
}, { immediate: true })

// ✅ ДОДАНО: Підписка на глобальні зміни коментарів
let unsubscribe = null

onMounted(() => {
  // Перевіряємо чи є збережена кількість коментарів
  const cached = getCommentsCount(props.post.id)
  if (cached !== undefined) {
    localCommentsCount.value = cached
  }
  
  // Підписуємось на оновлення
  unsubscribe = subscribe((postId, count) => {
    if (postId === props.post.id) {
      localCommentsCount.value = count
    }
  })
})

onUnmounted(() => {
  // Відписуємось при знищенні компонента
  if (unsubscribe) {
    unsubscribe()
  }
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    return format(new Date(dateString), 'd MMMM yyyy', { locale: uk })
  } catch {
    return dateString
  }
}

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}
</script>