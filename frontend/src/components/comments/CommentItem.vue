<template>
  <div class="comment-thread">
    <div class="comment-item bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm">

      <!-- Заголовок -->
      <div class="flex items-start justify-between mb-2">
        <div class="flex items-center gap-3">
          <img
            :src="author.avatar || '/default-avatar.png'"
            :alt="author.username"
            class="rounded-full object-cover flex-shrink-0"
            :class="depth === 0 ? 'w-9 h-9' : 'w-7 h-7'"
          />
          <div>
            <AuthorWithKarma
              size="md"
              :username="comment.author_info.username"
              :karma="comment.author_info.karma_points || 0"
              :level="comment.author_info.karma_level || 1"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400">
              {{ formatDate(comment.created_at) }}
            </p>
          </div>
        </div>

        <div v-if="isOwner" class="flex gap-3 text-sm">
          <button @click="$emit('edit', comment)" class="text-blue-600 hover:text-blue-800 dark:text-blue-400">
            Редагувати
          </button>
          <button @click="$emit('delete', comment.id)" class="text-red-600 hover:text-red-800 dark:text-red-400">
            Видалити
          </button>
        </div>
      </div>

      <!-- Контент -->
      <p class="mb-3 text-gray-800 dark:text-gray-200 whitespace-pre-wrap text-sm leading-relaxed">
        <span v-if="comment.reply_to_username" class="text-blue-500 font-semibold">
          @{{ comment.reply_to_username }}&nbsp;
        </span>{{ comment.content }}
      </p>

      <!-- Дії -->
      <div class="flex items-center gap-4 text-sm">
        <button
          v-if="isAuthenticated"
          @click="toggleReplyForm"
          class="flex items-center gap-1 transition"
          :class="showReplyForm
            ? 'text-blue-600 dark:text-blue-400'
            : 'text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400'"
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

        <!-- Згорнути/розгорнути гілку -->
        <button
          v-if="comment.children && comment.children.length"
          @click="collapsed = !collapsed"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition text-xs"
        >
          {{ collapsed ? `▶ показати ${countDescendants(comment)} відповідей` : '▲ згорнути' }}
        </button>
      </div>
    </div>

    <!-- Форма відповіді -->
    <Transition name="reply-slide">
      <div v-if="showReplyForm" class="mt-2" :style="indentStyle">
        <CommentForm
          :post-id="postId"
          :reply-to="comment"
          :is-authenticated="isAuthenticated"
          :loading="submitting"
          @submit="handleReplySubmit"
          @cancel="showReplyForm = false"
        />
      </div>
    </Transition>

    <!-- Дочірні коментарі (рекурсія) -->
    <Transition name="collapse">
      <div
        v-if="!collapsed && comment.children && comment.children.length"
        class="mt-2 space-y-2"
        :style="indentStyle"
      >
        <!-- Вертикальна лінія для візуальної вкладеності -->
        <div class="relative pl-4 border-l-2" :class="borderColor">
          <div class="space-y-2">
            <CommentItem
              v-for="child in comment.children"
              :key="`c-${child.id}`"
              :comment="child"
              :post-id="postId"
              :current-user-id="currentUserId"
              :is-authenticated="isAuthenticated"
              :depth="Math.min(depth + 1, MAX_VISUAL_DEPTH)"
              @edit="$emit('edit', $event)"
              @delete="$emit('delete', $event)"
              @new-reply="$emit('new-reply', $event)"
            />
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import LikeButton from '@/components/ui/LikeButton.vue'
import AuthorWithKarma from '@/components/ui/KarmaBadge.vue'
import CommentForm from './CommentForm.vue'
import { commentsAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

// Після цього рівня відступ більше не збільшується (як Reddit)
const MAX_VISUAL_DEPTH = 5

const props = defineProps({
  comment:         { type: Object,  required: true },
  postId:          { type: Number,  required: true },
  currentUserId:   { type: Number,  default: null },
  isAuthenticated: { type: Boolean, default: false },
  depth:           { type: Number,  default: 0 },
})

const emit = defineEmits(['edit', 'delete', 'new-reply'])

const toast = useToast()
const showReplyForm = ref(false)
const submitting    = ref(false)
const collapsed     = ref(false)

const author  = computed(() => props.comment.author_info || {})
const isOwner = computed(() => {
  const aid = author.value.id || props.comment.author_id
  return props.currentUserId && aid === props.currentUserId
})

// Відступ зменшується після MAX_VISUAL_DEPTH
const indentStyle = computed(() => {
  if (props.depth >= MAX_VISUAL_DEPTH) return {}
  return {}  // відступ робиться через border-l + pl у батьківському div
})

// Кольори лінії по глибині (циклічно)
const BORDER_COLORS = [
  'border-blue-200 dark:border-blue-800',
  'border-purple-200 dark:border-purple-800',
  'border-green-200 dark:border-green-800',
  'border-orange-200 dark:border-orange-800',
  'border-pink-200 dark:border-pink-800',
]
const borderColor = computed(() => BORDER_COLORS[props.depth % BORDER_COLORS.length])

// Рахуємо всіх нащадків для кнопки "згорнути"
function countDescendants(comment) {
  if (!comment.children?.length) return 0
  return comment.children.reduce((sum, c) => sum + 1 + countDescendants(c), 0)
}

const toggleReplyForm = () => { showReplyForm.value = !showReplyForm.value }

const handleReplySubmit = async (payload) => {
  submitting.value = true
  try {
    const { data: newComment } = await commentsAPI.create({
      post:    props.postId,
      content: payload.content,
      parent:  props.comment.id,  // ← вказуємо на ЦЕЙ коментар, не root
    })

    newComment.reply_to_username = props.comment.author_info?.username
    newComment.children = []

    emit('new-reply', {
      reply:    newComment,
      parentId: props.comment.id,
    })

    showReplyForm.value = false
    toast.success('Відповідь додано')
  } catch (e) {
    toast.error('Помилка при відправці відповіді')
    console.error(e)
  } finally {
    submitting.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins  = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays  = Math.floor(diffMs / 86400000)

  if (diffMins < 1)  return 'щойно'
  if (diffMins < 60) return `${diffMins} хв тому`
  if (diffHours < 24) return `${diffHours} год тому`
  if (diffDays < 7)  return `${diffDays} дн тому`

  return date.toLocaleDateString('uk-UA', {
    day: 'numeric', month: 'short',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined
  })
}
</script>

<style scoped>
.reply-slide-enter-active, .reply-slide-leave-active { transition: all 0.2s ease; }
.reply-slide-enter-from, .reply-slide-leave-to { opacity: 0; transform: translateY(-6px); }

.collapse-enter-active, .collapse-leave-active { transition: all 0.25s ease; }
.collapse-enter-from, .collapse-leave-to { opacity: 0; transform: translateY(-4px); }
</style>