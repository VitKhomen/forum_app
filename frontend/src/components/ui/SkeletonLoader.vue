<template>
  <!-- Пост карточка -->
  <div v-if="type === 'post-card'" class="bg-white dark:bg-gray-800 rounded-lg overflow-hidden shadow-md">
    <!-- Image -->
    <div class="aspect-video bg-gray-200 dark:bg-gray-700 animate-pulse" />
    <div class="p-5 space-y-3">
      <!-- Category + date -->
      <div class="flex gap-2">
        <div class="h-3 w-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div class="h-3 w-3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div class="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
      <!-- Title -->
      <div class="space-y-2">
        <div class="h-5 w-full bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div class="h-5 w-3/4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
      <!-- Excerpt -->
      <div class="space-y-1.5">
        <div class="h-3 w-full bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div class="h-3 w-full bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div class="h-3 w-2/3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
      <!-- Footer -->
      <div class="flex justify-between pt-2">
        <div class="h-5 w-24 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse" />
        <div class="flex gap-3">
          <div class="h-4 w-10 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          <div class="h-4 w-10 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        </div>
      </div>
    </div>
  </div>

  <!-- Деталь поста -->
  <div v-else-if="type === 'post-detail'" class="space-y-6">
    <!-- Main image -->
    <div class="w-full h-72 md:h-96 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse" />
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 md:p-8 space-y-6">
      <!-- Category + date -->
      <div class="flex gap-3">
        <div class="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div class="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
      <!-- Title -->
      <div class="space-y-3">
        <div class="h-8 w-full bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div class="h-8 w-2/3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
      <!-- Author -->
      <div class="flex items-center gap-3 pb-6 border-b border-gray-200 dark:border-gray-700">
        <div class="w-14 h-14 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse flex-shrink-0" />
        <div class="space-y-2">
          <div class="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          <div class="h-3 w-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        </div>
      </div>
      <!-- Content lines -->
      <div class="space-y-2">
        <div v-for="i in 8" :key="i"
          class="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"
          :style="{ width: i % 4 === 0 ? '60%' : '100%' }"
        />
      </div>
    </div>
  </div>

  <!-- Коментар -->
  <div v-else-if="type === 'comment'" class="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm space-y-3">
    <!-- Header -->
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse flex-shrink-0" />
      <div class="space-y-1.5">
        <div class="h-4 w-28 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
        <div class="h-3 w-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
    </div>
    <!-- Text -->
    <div class="space-y-1.5">
      <div class="h-3 w-full bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      <div class="h-3 w-full bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      <div class="h-3 w-1/2 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
    </div>
    <!-- Actions -->
    <div class="flex gap-4">
      <div class="h-3 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      <div class="h-3 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
    </div>
  </div>

  <!-- Профіль -->
  <div v-else-if="type === 'profile'" class="space-y-6">
    <!-- Шапка профілю -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div class="flex flex-col sm:flex-row items-center sm:items-start gap-6">
        <div class="w-24 h-24 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse flex-shrink-0" />
        <div class="flex-1 space-y-3 w-full">
          <div class="h-7 w-48 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          <div class="h-4 w-64 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          <div class="h-4 w-full bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          <div class="h-4 w-3/4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          <!-- Stats -->
          <div class="flex gap-6 pt-2">
            <div v-for="i in 3" :key="i" class="space-y-1">
              <div class="h-6 w-10 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              <div class="h-3 w-16 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Пости -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <SkeletonLoader v-for="i in 6" :key="i" type="post-card" />
    </div>
  </div>

  <!-- Сайдбар -->
  <div v-else-if="type === 'sidebar'" class="space-y-6">
    <!-- Теги -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 space-y-4">
      <div class="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      <div class="flex flex-wrap gap-2">
        <div
          v-for="i in 8" :key="i"
          class="h-7 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse"
          :style="{ width: `${50 + Math.random() * 50}px` }"
        />
      </div>
    </div>
    <!-- Популярні пости -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <div class="p-5 border-b border-gray-200 dark:border-gray-700">
        <div class="h-5 w-40 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      </div>
      <div class="divide-y divide-gray-100 dark:divide-gray-700">
        <div v-for="i in 5" :key="i" class="h-32 bg-gray-200 dark:bg-gray-700 animate-pulse" />
      </div>
    </div>
  </div>

  <!-- Лідерборд рядок -->
  <div v-else-if="type === 'leaderboard-row'" class="flex items-center gap-4 p-4 bg-white dark:bg-gray-800 rounded-lg">
    <div class="h-6 w-6 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
    <div class="w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse" />
    <div class="flex-1 space-y-1.5">
      <div class="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
      <div class="h-3 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
    </div>
    <div class="h-6 w-20 bg-gray-200 dark:bg-gray-700 rounded-full animate-pulse" />
  </div>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    required: true,
    // post-card | post-detail | comment | profile | sidebar | leaderboard-row
  },
})
</script>