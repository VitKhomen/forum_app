<template>
  <section class="mb-10">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
        {{ title }}
      </h2>
      <button
        v-if="$attrs.onSeeAll"
        @click="$emit('see-all')"
        class="text-xs text-amber-600 dark:text-amber-400 hover:text-amber-700 dark:hover:text-amber-300 font-semibold transition-colors flex items-center gap-1"
      >
        Всі <span aria-hidden>→</span>
      </button>
    </div>

    <!-- Скелетон -->
    <div v-if="loading" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
      <div
        v-for="i in 5"
        :key="i"
        class="aspect-[2/3] rounded-xl bg-gray-200 dark:bg-gray-800 animate-pulse"
      />
    </div>

    <!-- Контент -->
    <div v-else-if="items.length" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
      <MovieCard
        v-for="(item, i) in items"
        :key="item.id"
        :movie="item"
        :media-type="mediaType"
        :rank="showRank ? i + 1 : null"
      />
    </div>

    <!-- Порожньо -->
    <div v-else class="h-40 rounded-2xl bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-gray-400 text-sm">
      Немає даних
    </div>
  </section>
</template>

<script setup>
import MovieCard from './MovieCard.vue'

defineProps({
  title:     { type: String, required: true },
  items:     { type: Array,  default: () => [] },
  mediaType: { type: String, default: 'movie' },
  loading:   { type: Boolean, default: false },
  showRank:  { type: Boolean, default: false },
})

defineEmits(['see-all'])
</script>