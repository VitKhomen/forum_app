<template>
  <button
    @click="handleToggle"
    :disabled="loading"
    class="inline-flex items-center gap-1.5 transition-all"
    :class="[
      isBookmarked
        ? 'text-amber-500 dark:text-amber-400'
        : 'text-gray-400 dark:text-gray-500 hover:text-amber-500 dark:hover:text-amber-400',
      loading && 'opacity-50 cursor-not-allowed',
      sizeClasses
    ]"
    :title="isBookmarked ? 'Видалити із закладок' : 'Додати до закладок'"
  >
    <!-- Іконка закладки -->
    <svg
      :class="iconSizeClasses"
      viewBox="0 0 24 24"
      :fill="isBookmarked ? 'currentColor' : 'none'"
      stroke="currentColor"
      stroke-width="2"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        d="M5 4a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 20V4z"
      />
    </svg>

    <span v-if="!iconOnly" class="font-medium">
      {{ isBookmarked ? 'Збережено' : 'Зберегти' }}
    </span>
  </button>
</template>

<script setup>
import { ref, watch } from 'vue'
import { bookmarksAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const props = defineProps({
  postId: {
    type: Number,
    required: true
  },
  initialBookmarked: {
    type: Boolean,
    default: false
  },
  // Показувати тільки іконку без тексту
  iconOnly: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'md', // sm | md | lg
  }
})

const emit = defineEmits(['update'])

const authStore = useAuthStore()
const toast = useToast()

const isBookmarked = ref(props.initialBookmarked)
const loading = ref(false)

const sizeClasses = {
  sm: 'text-xs',
  md: 'text-sm',
  lg: 'text-base',
}[props.size]

const iconSizeClasses = {
  sm: 'w-3.5 h-3.5',
  md: 'w-5 h-5',
  lg: 'w-6 h-6',
}[props.size]

const handleToggle = async () => {
  if (!authStore.isAuthenticated) {
    toast.warning('Увійдіть щоб зберігати закладки')
    return
  }

  loading.value = true
  try {
    const { data } = await bookmarksAPI.toggle(props.postId)
    isBookmarked.value = data.bookmarked
    toast.success(data.message)
    emit('update', data.bookmarked)
  } catch (error) {
    console.error('Bookmark error:', error)
    toast.error('Помилка при збереженні')
  } finally {
    loading.value = false
  }
}

// Синхронізація з props
watch(() => props.initialBookmarked, (val) => {
  isBookmarked.value = val
})
</script>