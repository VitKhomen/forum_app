<template>
  <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <label
          v-if="replyTo"
          class="block text-sm text-gray-600 dark:text-gray-400 mb-2"
        >
          Відповідь на коментар від {{ replyTo.author_info?.username }}
        </label>

        <!-- Обгортка textarea з кнопкою emoji -->
        <div class="relative">
          <textarea
            ref="textareaRef"
            v-model="content"
            :placeholder="placeholder"
            rows="3"
            class="w-full px-4 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            :disabled="loading"
            @keydown="handleTextareaKeydown"
          ></textarea>

          <!-- Кнопка відкрити emoji picker -->
          <button
            ref="emojiTriggerRef"
            type="button"
            @click="togglePicker"
            class="absolute bottom-2 right-2 p-1 rounded-lg text-gray-400 hover:text-yellow-500 hover:bg-gray-100 dark:hover:bg-gray-700 transition-all"
            :class="{ 'text-yellow-500 bg-gray-100 dark:bg-gray-700': pickerOpen }"
            title="Додати емодзі"
            :disabled="loading"
          >
            <svg viewBox="0 0 24 24" class="w-5 h-5" fill="currentColor">
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="flex items-center justify-between">
        <span v-if="!isAuthenticated" class="text-sm text-gray-600 dark:text-gray-400">
          <RouterLink to="/login" class="text-blue-600 hover:underline">
            Увійдіть
          </RouterLink>
          , щоб залишити коментар
        </span>

        <div class="flex gap-2 ml-auto">
          <button
            v-if="replyTo || editComment"
            type="button"
            @click="handleCancel"
            class="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500 transition"
            :disabled="loading"
          >
            Скасувати
          </button>

          <button
            type="submit"
            :disabled="!canSubmit"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {{ loading ? 'Відправка...' : (isEditing ? 'Зберегти' : 'Надіслати') }}
          </button>
        </div>
      </div>
    </form>

    <!-- Emoji Picker -->
    <EmojiPicker
      v-model="pickerOpen"
      :anchor-el="emojiTriggerRef"
      @select="insertEmoji"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'
import EmojiPicker from '@/components/comments/EmojiPicker.vue'

const props = defineProps({
  postId:      { type: Number, required: true },
  replyTo:     { type: Object, default: null },
  editComment: { type: Object, default: null },
  isAuthenticated: { type: Boolean, default: false },
  loading:     { type: Boolean, default: false },
})

const emit = defineEmits(['submit', 'cancel'])

const content        = ref('')
const textareaRef    = ref(null)
const emojiTriggerRef = ref(null)
const pickerOpen     = ref(false)

const isEditing = computed(() => !!props.editComment)

const placeholder = computed(() => {
  if (props.replyTo) return `Відповісти ${props.replyTo.author_info?.username}...`
  return 'Напишіть ваш коментар...'
})

const canSubmit = computed(() =>
  props.isAuthenticated && content.value.trim().length > 0 && !props.loading
)

// ── Emoji ──────────────────────────────────────────────────────
const togglePicker = () => {
  pickerOpen.value = !pickerOpen.value
}

const insertEmoji = (emoji) => {
  const el = textareaRef.value
  if (!el) {
    content.value += emoji
    return
  }

  const start = el.selectionStart ?? content.value.length
  const end   = el.selectionEnd   ?? content.value.length

  content.value = content.value.slice(0, start) + emoji + content.value.slice(end)

  // Повертаємо фокус і ставимо курсор після emoji
  requestAnimationFrame(() => {
    el.focus()
    const pos = start + emoji.length
    el.setSelectionRange(pos, pos)
  })

  // Не закриваємо picker — як у Telegram
}

// Закриваємо picker при Escape у textarea
const handleTextareaKeydown = (e) => {
  if (e.key === 'Escape' && pickerOpen.value) {
    pickerOpen.value = false
    e.stopPropagation()
  }
}

// ── Submit / Cancel ───────────────────────────────────────────
const handleSubmit = () => {
  if (!canSubmit.value) return

  pickerOpen.value = false

  const data = {
    content: content.value.trim(),
    post: props.postId,
  }

  if (props.replyTo) data.parent = props.replyTo.id

  if (isEditing.value) {
    emit('submit', { id: props.editComment.id, data })
  } else {
    emit('submit', data)
  }
}

const handleCancel = () => {
  content.value = ''
  pickerOpen.value = false
  emit('cancel')
}

watch(() => props.editComment, (newVal) => {
  if (newVal) content.value = newVal.content
  else        content.value = ''
}, { immediate: true })
</script>