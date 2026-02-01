<template>
  <div class="comment-item bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
    <!-- Заголовок коментаря -->
    <div class="flex items-start justify-between mb-2">
      <div class="flex items-center gap-3">
        <img
          :src="author.avatar || '/default-avatar.png'"
          :alt="author.username"
          class="w-10 h-10 rounded-full object-cover"
        />
        <div>
          <p class="font-semibold text-gray-900 dark:text-white">
            {{ author.username || author.full_name || 'Анонім' }}
          </p>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ formatDate(comment.created_at) }}
          </p>
        </div>
      </div>

      <div v-if="isOwner" class="flex gap-3 text-sm">
        <button
          @click="$emit('edit', comment)"
          class="text-blue-600 hover:text-blue-800 dark:text-blue-400"
        >
          Редагувати
        </button>
        <button
          @click="$emit('delete', comment.id)"
          class="text-red-600 hover:text-red-800 dark:text-red-400"
        >
          Видалити
        </button>
      </div>
    </div>

    <!-- Контент -->
    <p class="mb-3 text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
      {{ comment.content }}
    </p>

    <!-- Дії -->
    <div class="flex items-center gap-4 text-sm">
      <button
        v-if="!isReply"
        @click="$emit('reply', comment)"
        class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition"
      >
        💬 Відповісти
      </button>

      <LikeButton
        content-type="comment"
        :object-id="comment.id"
        :initial-likes-count="comment.likes_count || 0"
        :initial-is-liked="comment.is_liked || false"
        class="!px-2 !py-1 text-xs"
      />

      <button
        v-if="!isReply && comment.replies_count"
        @click="$emit('toggle-replies')"
        class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition"
      >
        {{ showReplies ? '▼' : '▶' }} {{ comment.replies_count }}
        {{ comment.replies_count === 1 ? 'відповідь' : 'відповідей' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LikeButton from '@/components/ui/LikeButton.vue'

const props = defineProps({
  comment: { type: Object, required: true },
  currentUserId: { type: Number, default: null },
  isReply: { type: Boolean, default: false },
  showReplies: { type: Boolean, default: false }
})

defineEmits(['reply', 'edit', 'delete', 'toggle-replies'])

// Автор (спрощуємо доступ)
const author = computed(() => props.comment.author_info || props.comment.author || {})

// Чи власник коментаря
const isOwner = computed(() => {
  const authorId = author.value.id || props.comment.author_id
  return props.currentUserId && authorId === props.currentUserId
})

// Форматування дати (спрощено)
const formatDate = (dateString) => {
  if (!dateString) return ''

  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return 'щойно'
  if (diffMins < 60) return `${diffMins} хв тому`
  if (diffHours < 24) return `${diffHours} год тому`
  if (diffDays < 7) return `${diffDays} дн тому`

  return date.toLocaleDateString('uk-UA', {
    day: 'numeric',
    month: 'short',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}
</script>