<template>
  <div
    :class="[
      'inline-flex items-center gap-1 transition-all',
      !readonly && isAuthenticated && !loading ? 'cursor-pointer' : 'cursor-default',
      isLiked ? 'text-red-600 dark:text-red-400' : 'text-gray-600 dark:text-gray-400',
      loading && 'opacity-50',
      readonly && 'pointer-events-none'
    ]"
    @click="!readonly && handleToggle()"
    :title="readonly ? '' : (!isAuthenticated ? 'Увійдіть щоб лайкнути' : '')"
  >
    <!-- Іконка серця -->
    <HeartIcon 
      :class="[
        'w-4 h-4 transition-all duration-200',
        isLiked ? 'fill-current scale-110' : 'scale-100',
        loading && 'animate-pulse'
      ]" 
    />

    <!-- Кількість лайків — показуємо тільки якщо не readonly або хочеш завжди -->
    <span v-if="!hideCount" class="text-sm font-medium">
      {{ likesCount }}
    </span>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { HeartIcon } from '@heroicons/vue/24/outline'  // або /outline, якщо хочеш
import { likesAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const props = defineProps({
  contentType: {
    type: String,
    required: true,
    validator: value => ['post', 'comment'].includes(value)
  },
  objectId: {
    type: Number,
    required: true
  },
  initialLikesCount: {
    type: Number,
    default: 0
  },
  initialIsLiked: {
    type: Boolean,
    default: false
  },
  // Новий пропс: режим "тільки перегляд" (без кліку)
  readonly: {
    type: Boolean,
    default: false
  },
  // Чи ховати кількість лайків (для мінімалістичного вигляду)
  hideCount: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update'])

const authStore = useAuthStore()
const toast = useToast()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const loading = ref(false)
const likesCount = ref(props.initialLikesCount)
const isLiked = ref(props.initialIsLiked)

const handleToggle = async () => {
  if (props.readonly) return
  if (!isAuthenticated.value) {
    toast.warning('Увійдіть щоб лайкнути')
    return
  }

  try {
    loading.value = true
    const { data } = await likesAPI.toggle(props.contentType, props.objectId)
    
    likesCount.value = data.likes_count
    isLiked.value = data.liked
    
    emit('update', { likesCount: data.likes_count, isLiked: data.liked })
  } catch (error) {
    console.error('Error toggling like:', error)
    toast.error('Помилка при зміні лайка')
  } finally {
    loading.value = false
  }
}

// Синхронізація з props (якщо батьківський компонент оновлює)
watch(() => props.initialLikesCount, (newVal) => likesCount.value = newVal)
watch(() => props.initialIsLiked, (newVal) => isLiked.value = newVal)
</script>

<style scoped>
/* Додаткові стилі для readonly-режиму (опціонально) */
.readonly-heart {
  opacity: 0.8;
}
</style>