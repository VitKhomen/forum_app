<template>
  <div class="bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-xl p-5 space-y-4">

    <div class="flex items-center gap-2">
      <span class="text-lg">📊</span>
      <h3 class="font-semibold text-gray-900 dark:text-white text-base leading-snug">
        {{ localPoll.question }}
      </h3>
    </div>

    <!-- Форма голосування -->
    <div v-if="!hasVoted && isAuthenticated" class="space-y-2">
      <label
        v-for="option in localPoll.options"
        :key="option.id"
        class="flex items-center gap-3 p-3 rounded-lg border-2 cursor-pointer transition-all"
        :class="selected.includes(option.id)
          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
          : 'border-gray-200 dark:border-gray-600 hover:border-blue-300 dark:hover:border-blue-600'"
      >
        <!-- checkbox — multiple, v-model масив -->
        <input
          v-if="localPoll.is_multiple"
          type="checkbox"
          :value="option.id"
          v-model="selected"
          class="accent-blue-600 w-4 h-4 flex-shrink-0"
        />
        <!-- radio — single, v-model через computed -->
        <input
          v-else
          type="radio"
          :value="option.id"
          v-model="selectedSingle"
          class="accent-blue-600 w-4 h-4 flex-shrink-0"
        />
        <span class="text-sm text-gray-700 dark:text-gray-300">{{ option.text }}</span>
      </label>

      <button
        @click="vote"
        :disabled="!selected.length || loading"
        class="w-full py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium
               hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
      >
        {{ loading ? 'Голосуємо...' : 'Проголосувати' }}
      </button>
    </div>

    <!-- Результати -->
    <div v-else class="space-y-3">
      <div v-for="option in localPoll.options" :key="option.id" class="space-y-1">
        <div class="flex justify-between items-center text-sm">
          <span class="text-gray-700 dark:text-gray-300 flex items-center gap-1.5">
            <span
              v-if="localPoll.user_voted?.includes(option.id)"
              class="text-blue-500 font-bold"
            >✓</span>
            {{ option.text }}
          </span>
          <span class="text-gray-500 dark:text-gray-400 font-medium tabular-nums">
            {{ option.vote_percent }}%
          </span>
        </div>

        <div class="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            class="h-full rounded-full transition-all duration-700"
            :class="localPoll.user_voted?.includes(option.id)
              ? 'bg-blue-500'
              : 'bg-gray-400 dark:bg-gray-500'"
            :style="{ width: option.vote_percent + '%' }"
          />
        </div>

        <p class="text-xs text-gray-400">{{ option.votes_count }} голосів</p>
      </div>

      <button
        v-if="hasVoted && isAuthenticated"
        @click="unvote"
        :disabled="loading"
        class="text-xs text-gray-400 hover:text-red-500 transition underline"
      >
        Скасувати голос
      </button>
    </div>

    <!-- Футер -->
    <div class="text-xs text-gray-400 pt-1 border-t border-gray-200 dark:border-gray-700">
      Всього голосів: {{ localPoll.total_votes }}
    </div>

    <!-- Не авторизований -->
    <p v-if="!isAuthenticated" class="text-sm text-gray-500 dark:text-gray-400 text-center">
      <RouterLink to="/login" class="text-blue-600 hover:underline">Увійдіть</RouterLink>
      , щоб проголосувати
    </p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { pollsAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

const props = defineProps({
  poll:            { type: Object,  required: true },
  isAuthenticated: { type: Boolean, default: false },
})

const emit = defineEmits(['update'])
const toast = useToast()

const localPoll = ref({ ...props.poll, options: [...props.poll.options] })
// ← завжди масив, навіть для radio
const selected  = ref([])
const loading   = ref(false)

const hasVoted = computed(() => localPoll.value.user_voted?.length > 0)

// ── для radio — окремий ref щоб v-model працював ──────────────
const selectedSingle = computed({
  get: () => selected.value[0] ?? null,
  set: (val) => { selected.value = val !== null ? [val] : [] }
})

const vote = async () => {
  loading.value = true
  try {
    const { data } = await pollsAPI.vote(localPoll.value.id, selected.value)
    localPoll.value = data
    selected.value  = []
    emit('update', data)
    toast.success('Голос зараховано!')
  } catch (e) {
    toast.error(e.response?.data?.error || 'Помилка голосування')
  } finally {
    loading.value = false
  }
}

const unvote = async () => {
  loading.value = true
  try {
    const { data } = await pollsAPI.unvote(localPoll.value.id)
    localPoll.value = data
    emit('update', data)
    toast.info('Голос скасовано')
  } catch {
    toast.error('Помилка')
  } finally {
    loading.value = false
  }
}
</script>