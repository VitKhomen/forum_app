<template>
  <div class="comment-item bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">
    <!-- Comment Header -->
    <div class="flex items-start justify-between mb-2">
      <div class="flex items-center gap-3">
        <img
          :src="comment.author_info?.avatar || '/default-avatar.png'"
          :alt="comment.author_info?.username"
          class="w-10 h-10 rounded-full object-cover"
        />
        <div>
          <p class="font-semibold text-gray-900 dark:text-white">
            {{ comment.author_info?.username || comment.author_info?.full_name }}
          </p>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            {{ formatDate(comment.created_at) }}
          </p>
        </div>
      </div>

      <!-- Actions Menu -->
      <div v-if="isOwner" class="flex gap-2">
        <button
          @click="$emit('edit', comment)"
          class="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400"
        >
          Редагувати
        </button>
        <button
          @click="$emit('delete', comment.id)"
          class="text-sm text-red-600 hover:text-red-800 dark:text-red-400"
        >
          Видалити
        </button>
      </div>
    </div>

    <!-- Comment Content -->
    <div class="mb-3">
      <p class="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
        {{ comment.content }}
      </p>
    </div>

    <!-- Comment Actions -->
    <div class="flex items-center gap-4 text-sm">
      <button
        v-if="!isReply && hasValidId"
        @click="$emit('reply', comment)"
        class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition"
      >
        💬 Відповісти
      </button>
      
      <!-- кнопка лайка -->
      <LikeButton
        content-type="comment"
        :object-id="comment.id"
        :initial-likes-count="comment.likes_count || 0"
        :initial-is-liked="comment.is_liked || false"
        class="!px-2 !py-1 text-xs"
      />

      <button
        v-if="!isReply && hasValidId && comment.replies_count > 0"
        @click="$emit('toggle-replies')"
        class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition"
      >
        {{ showReplies ? '▼' : '▶' }} 
        {{ comment.replies_count }} 
        {{ comment.replies_count === 1 ? 'відповідь' : 'відповідей' }}
      </button>

      <!-- Loading indicator for new comments -->
      <span 
        v-if="!hasValidId"
        class="text-xs text-gray-400 dark:text-gray-500"
      >
        Збереження...
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import LikeButton from '@/components/ui/LikeButton.vue'

const props = defineProps({
  comment: {
    type: Object,
    required: true
  },
  currentUserId: {
    type: Number,
    default: null
  },
  isReply: {
    type: Boolean,
    default: false
  },
  showReplies: {
    type: Boolean,
    default: false
  }
})

defineEmits(['reply', 'edit', 'delete', 'toggle-replies'])

const isOwner = computed(() => {
  return props.currentUserId && props.comment.author_info?.id === props.currentUserId
})

// Перевіряємо чи коментар має валідний ID
const hasValidId = computed(() => {
  const id = props.comment?.id
  return id && !isNaN(Number(id)) && Number(id) > 0
})

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