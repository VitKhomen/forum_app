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

      <!-- Контент з рендером цитат -->
      <div class="mb-3 text-sm leading-relaxed">
        <template v-for="(block, i) in parsedContent" :key="i">
          <!-- Блок цитати -->
          <blockquote
            v-if="block.type === 'quote'"
            class="border-l-4 border-blue-400 dark:border-blue-500 bg-blue-50 dark:bg-blue-900/20 pl-3 py-1 my-2 rounded-r text-gray-600 dark:text-gray-400 italic text-xs"
          >
            {{ block.text }}
          </blockquote>
          <!-- Звичайний текст -->
          <p v-else class="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
            <span v-if="block.mention" class="text-blue-500 font-semibold">@{{ block.mention }}&nbsp;</span>{{ block.text }}
          </p>
        </template>
      </div>

      <!-- Дії -->
      <div class="flex items-center gap-4 text-sm">
        <button
          v-if="isAuthenticated"
          @click="startReply(false)"
          class="flex items-center gap-1 transition"
          :class="showReplyForm && !withQuote
            ? 'text-blue-600 dark:text-blue-400'
            : 'text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400'"
        >
          💬 Відповісти
        </button>

        <!-- Кнопка цитування -->
        <button
          v-if="isAuthenticated"
          @click="startReply(true)"
          class="flex items-center gap-1 transition"
          :class="showReplyForm && withQuote
            ? 'text-amber-600 dark:text-amber-400'
            : 'text-gray-500 dark:text-gray-400 hover:text-amber-600 dark:hover:text-amber-400'"
          title="Відповісти з цитатою"
        >
          ❝ Цитувати
        </button>

        <LikeButton
          content-type="comment"
          :object-id="comment.id"
          :initial-likes-count="comment.likes_count || 0"
          :initial-is-liked="comment.is_liked || false"
          class="!px-2 !py-1 text-xs"
        />

        <button
          v-if="comment.children && comment.children.length"
          @click="collapsed = !collapsed"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition text-xs ml-auto"
        >
          {{ collapsed ? `▶ ${countDescendants(comment)} відп.` : '▲ згорнути' }}
        </button>
      </div>
    </div>

    <!-- Форма відповіді -->
    <Transition name="reply-slide">
      <div v-if="showReplyForm" class="mt-2" :style="indentStyle">
        <CommentForm
          :post-id="postId"
          :reply-to="comment"
          :quote="withQuote ? quoteText : ''"
          :is-authenticated="isAuthenticated"
          :loading="submitting"
          @submit="handleReplySubmit"
          @cancel="showReplyForm = false"
        />
      </div>
    </Transition>

    <!-- Дочірні коментарі -->
    <Transition name="collapse">
      <div
        v-if="!collapsed && comment.children && comment.children.length"
        class="mt-2 space-y-2"
      >
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
const withQuote     = ref(false)
const submitting    = ref(false)
const collapsed     = ref(false)

const author  = computed(() => props.comment.author_info || {})
const isOwner = computed(() => {
  const aid = author.value.id || props.comment.author_id
  return props.currentUserId && aid === props.currentUserId
})

// Текст для цитати — перші 120 символів без рядків цитат
const quoteText = computed(() => {
  const raw = props.comment.content || ''
  // Прибираємо вже існуючі цитати (рядки що починаються з >)
  const withoutQuotes = raw.split('\n').filter(l => !l.startsWith('>')).join('\n').trim()
  const preview = withoutQuotes.slice(0, 120)
  return preview + (withoutQuotes.length > 120 ? '…' : '')
})

// Парсимо контент: рядки що починаються з > — blockquote, решта — текст
const parsedContent = computed(() => {
  const lines = (props.comment.content || '').split('\n')
  const blocks = []
  let currentText = []
  let currentQuote = []

  const flushText = () => {
    if (currentText.length) {
      const text = currentText.join('\n').trim()
      if (text) {
        // Перевіряємо чи є @mention на початку
        const mentionMatch = text.match(/^@(\S+)\s?(.*)$/s)
        if (mentionMatch) {
          blocks.push({ type: 'text', mention: mentionMatch[1], text: mentionMatch[2] })
        } else {
          blocks.push({ type: 'text', text })
        }
      }
      currentText = []
    }
  }
  const flushQuote = () => {
    if (currentQuote.length) {
      blocks.push({ type: 'quote', text: currentQuote.join('\n') })
      currentQuote = []
    }
  }

  lines.forEach(line => {
    if (line.startsWith('>')) {
      flushText()
      currentQuote.push(line.slice(1).trim())
    } else {
      flushQuote()
      currentText.push(line)
    }
  })

  flushText()
  flushQuote()

  return blocks
})

const BORDER_COLORS = [
  'border-blue-200 dark:border-blue-800',
  'border-purple-200 dark:border-purple-800',
  'border-green-200 dark:border-green-800',
  'border-orange-200 dark:border-orange-800',
  'border-pink-200 dark:border-pink-800',
]
const borderColor = computed(() => BORDER_COLORS[props.depth % BORDER_COLORS.length])

function countDescendants(comment) {
  if (!comment.children?.length) return 0
  return comment.children.reduce((sum, c) => sum + 1 + countDescendants(c), 0)
}

const startReply = (quote) => {
  if (showReplyForm.value && withQuote.value === quote) {
    showReplyForm.value = false
    return
  }
  withQuote.value = quote
  showReplyForm.value = true
}

const handleReplySubmit = async (payload) => {
  submitting.value = true
  try {
    const { data: newComment } = await commentsAPI.create({
      post:    props.postId,
      content: payload.content,
      parent:  props.comment.id,
    })

    newComment.children = []

    emit('new-reply', {
      reply:    newComment,
      parentId: props.comment.id,
    })

    showReplyForm.value = false
    toast.success('Відповідь додано')
  } catch (e) {
    toast.error('Помилка при відправці')
    console.error(e)
  } finally {
    submitting.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diffMs    = now - date
  const diffMins  = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays  = Math.floor(diffMs / 86400000)
  if (diffMins < 1)   return 'щойно'
  if (diffMins < 60)  return `${diffMins} хв тому`
  if (diffHours < 24) return `${diffHours} год тому`
  if (diffDays < 7)   return `${diffDays} дн тому`
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