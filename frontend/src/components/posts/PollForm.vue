<!-- frontend/src/components/posts/PollForm.vue -->
<template>
  <div class="space-y-4 p-4 bg-blue-50 dark:bg-blue-900/10 border border-blue-200 dark:border-blue-800 rounded-lg">
    <div class="flex items-center justify-between">
      <h3 class="font-semibold text-gray-900 dark:text-white flex items-center gap-2">
        📊 Опитування
      </h3>
      <button type="button" @click="$emit('remove')"
        class="text-gray-400 hover:text-red-500 transition text-sm">
        Видалити
      </button>
    </div>

    <!-- Питання -->
    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        Питання *
      </label>
      <input
        v-model="localPoll.question"
        type="text"
        placeholder="Про що питаємо?"
        maxlength="500"
        class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
               bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm
               focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>

    <!-- Варіанти -->
    <div class="space-y-2">
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Варіанти відповіді (мін 2, макс 10)
      </label>

      <div v-for="(option, index) in localPoll.options" :key="index" class="flex items-center gap-2">
        <input
          v-model="localPoll.options[index]"
          type="text"
          :placeholder="`Варіант ${index + 1}`"
          maxlength="200"
          class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm
                 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          v-if="localPoll.options.length > 2"
          type="button"
          @click="removeOption(index)"
          class="text-red-400 hover:text-red-600 transition p-1"
        >✕</button>
      </div>

      <button
        v-if="localPoll.options.length < 10"
        type="button"
        @click="addOption"
        class="text-sm text-blue-600 dark:text-blue-400 hover:underline"
      >
        + Додати варіант
      </button>
    </div>

    <!-- Тільки кілька відповідей -->
    <label class="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 cursor-pointer">
      <input v-model="localPoll.is_multiple" type="checkbox" class="accent-blue-600" />
      Дозволити кілька відповідей
    </label>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue', 'remove'])

const localPoll = reactive({
  question:    props.modelValue?.question    || '',
  options:     props.modelValue?.options     || ['', ''],
  is_multiple: props.modelValue?.is_multiple || false,
})

const addOption    = () => localPoll.options.push('')
const removeOption = (i) => localPoll.options.splice(i, 1)

watch(localPoll, (val) => emit('update:modelValue', { ...val }), { deep: true })
</script>