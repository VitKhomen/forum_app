<template>
  <!-- Кнопка скарги -->
  <button
    @click="openModal"
    class="inline-flex items-center gap-1 text-xs transition-colors"
    :class="alreadyReported
      ? 'text-red-400 dark:text-red-500 cursor-default'
      : 'text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400'"
    :title="alreadyReported ? 'Ви вже подали скаргу' : 'Поскаржитись'"
    :disabled="alreadyReported"
  >
    <FlagIcon class="w-3.5 h-3.5" />
    <span v-if="!iconOnly">
      {{ alreadyReported ? 'Скарга подана' : 'Поскаржитись' }}
    </span>
  </button>

  <!-- Модальне вікно -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="showModal"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
        @click.self="closeModal"
      >
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-md p-6">

          <!-- Заголовок -->
          <div class="flex items-center justify-between mb-5">
            <h3 class="text-lg font-bold text-gray-900 dark:text-white">
              ⚑ Поскаржитись
            </h3>
            <button
              @click="closeModal"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <!-- Причина -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Причина скарги *
            </label>
            <div class="space-y-2">
              <label
                v-for="opt in reasonOptions"
                :key="opt.value"
                class="flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-all"
                :class="selectedReason === opt.value
                  ? 'border-red-400 bg-red-50 dark:bg-red-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300'"
              >
                <input
                  type="radio"
                  :value="opt.value"
                  v-model="selectedReason"
                  class="accent-red-500"
                />
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  {{ opt.icon }} {{ opt.label }}
                </span>
              </label>
            </div>
          </div>

          <!-- Коментар -->
          <div class="mb-5">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Коментар (необовʼязково)
            </label>
            <textarea
              v-model="reportComment"
              rows="3"
              maxlength="500"
              placeholder="Опишіть детальніше..."
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-xl
                     bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm
                     focus:outline-none focus:ring-2 focus:ring-red-400 resize-none"
            />
            <p class="text-xs text-gray-400 mt-1 text-right">
              {{ reportComment.length }}/500
            </p>
          </div>

          <!-- Кнопки -->
          <div class="flex gap-3">
            <button
              @click="submitReport"
              :disabled="!selectedReason || loading"
              class="flex-1 py-2.5 bg-red-500 hover:bg-red-600 text-white rounded-xl
                     font-medium text-sm transition-colors
                     disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ loading ? 'Відправляємо...' : 'Подати скаргу' }}
            </button>
            <button
              @click="closeModal"
              class="px-5 py-2.5 border border-gray-200 dark:border-gray-600
                     text-gray-700 dark:text-gray-300 rounded-xl text-sm
                     hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            >
              Скасувати
            </button>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { moderationAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { FlagIcon } from '@heroicons/vue/24/solid'

const props = defineProps({
  contentType:    { type: String,  required: true }, // 'post' | 'comment'
  objectId:       { type: Number,  required: true },
  iconOnly:       { type: Boolean, default: false },
  initialReported:{ type: Boolean, default: false },
})

const emit = defineEmits(['reported'])

const authStore = useAuthStore()
const toast     = useToast()

const showModal      = ref(false)
const selectedReason = ref('')
const reportComment  = ref('')
const loading        = ref(false)
const alreadyReported = ref(props.initialReported)

const reasonOptions = [
  { value: 'spam',       icon: '📢', label: 'Спам' },
  { value: 'hate',       icon: '🤬', label: 'Ненависть / образи' },
  { value: 'misleading', icon: '❌', label: 'Дезінформація' },
  { value: 'nsfw',       icon: '🔞', label: 'Небажаний контент' },
  { value: 'other',      icon: '❓', label: 'Інше' },
]

const openModal = () => {
  if (!authStore.isAuthenticated) {
    toast.warning('Увійдіть щоб поскаржитись')
    return
  }
  if (alreadyReported.value) return
  showModal.value = true
}

const closeModal = () => {
  showModal.value  = false
  selectedReason.value = ''
  reportComment.value  = ''
}

const submitReport = async () => {
  if (!selectedReason.value) return
  loading.value = true
  try {
    await moderationAPI.report(
      props.contentType,
      props.objectId,
      selectedReason.value,
      reportComment.value
    )
    alreadyReported.value = true
    emit('reported')
    closeModal()
    toast.success('Скаргу прийнято. Дякуємо!')
  } catch {
    toast.error('Помилка при відправці скарги')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.2s ease; }
.modal-fade-enter-from,  .modal-fade-leave-to      { opacity: 0; }
</style>