<template>
  <button
    @click="handleToggle"
    :disabled="loading || !isAuthenticated"
    :class="[
      'inline-flex items-center gap-1 transition-all',
      isLiked
        ? 'text-red-600 dark:text-red-400'
        : 'text-gray-600 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400',
      loading && 'opacity-50 cursor-not-allowed',
      !isAuthenticated && 'cursor-not-allowed opacity-60'
    ]"
    :title="!isAuthenticated ? 'Увійдіть щоб лайкнути' : ''"
  >
    <HeartIcon 
      :class="[
        'w-4 h-4 transition-all',
        isLiked ? 'fill-current scale-110' : '',
        loading && 'animate-pulse'
      ]" 
    />
    <span class="text-sm">{{ likesCount }}</span>
  </button>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { HeartIcon } from '@heroicons/vue/24/outline'
import { likesAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const props = defineProps({
  contentType: {
    type: String,
    required: true,
    validator: (value) => ['post', 'comment'].includes(value)
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

// Синхронізація з props
watch(() => props.initialLikesCount, (newVal) => {
  likesCount.value = newVal
})

watch(() => props.initialIsLiked, (newVal) => {
  isLiked.value = newVal
})
</script>