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
        
        <textarea
          v-model="content"
          :placeholder="placeholder"
          rows="3"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          :disabled="loading"
        ></textarea>
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
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  postId: {
    type: Number,
    required: true
  },
  replyTo: {
    type: Object,
    default: null
  },
  editComment: {
    type: Object,
    default: null
  },
  isAuthenticated: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const content = ref('')

const isEditing = computed(() => !!props.editComment)

const placeholder = computed(() => {
  if (props.replyTo) {
    return `Відповісти ${props.replyTo.author_info?.username}...`
  }
  return 'Напишіть ваш коментар...'
})

const canSubmit = computed(() => {
  return props.isAuthenticated && content.value.trim().length > 0 && !props.loading
})

const handleSubmit = () => {
  if (!canSubmit.value) return

  const data = {
    content: content.value.trim(),
    post: props.postId
  }

  if (props.replyTo) {
    data.parent = props.replyTo.id
  }

  if (isEditing.value) {
    emit('submit', { id: props.editComment.id, data })
  } else {
    emit('submit', data)
  }
  
  // Форма очиститься автоматично через key в батьківському компоненті
}

const handleCancel = () => {
  content.value = ''
  emit('cancel')
}

// Заповнюємо форму при редагуванні
watch(() => props.editComment, (newVal) => {
  if (newVal) {
    content.value = newVal.content
  } else {
    content.value = ''
  }
}, { immediate: true })
</script>