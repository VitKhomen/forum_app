<template>
  <RouterLink
    :to="{ name: mediaType === 'movie' ? 'movie-detail' : 'tv-detail', params: { id: movie.id } }"
    class="group relative block focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-400 rounded-xl"
  >
    <!-- Постер -->
    <div class="relative aspect-[2/3] rounded-xl overflow-hidden bg-gray-200 dark:bg-gray-800 shadow-md group-hover:shadow-2xl transition-all duration-300">

      <!-- Зображення -->
      <img
        v-if="posterUrl"
        :src="posterUrl"
        :alt="title"
        class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        loading="lazy"
      />
      <div v-else class="w-full h-full flex flex-col items-center justify-center gap-2 text-gray-400 dark:text-gray-600">
        <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
        </svg>
        <span class="text-xs">Без постера</span>
      </div>

      <!-- Overlay з градієнтом при ховері -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <div class="absolute bottom-0 left-0 right-0 p-3">
          <p v-if="movie.overview" class="text-white/80 text-xs line-clamp-3 leading-relaxed">
            {{ movie.overview }}
          </p>
          <div class="flex items-center gap-2 mt-2">
            <span class="inline-flex items-center gap-1 bg-amber-400 text-gray-900 text-xs font-bold px-2 py-0.5 rounded-full">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
              {{ movie.vote_average ? movie.vote_average.toFixed(1) : '—' }}
            </span>
            <span class="text-white/60 text-xs">{{ year }}</span>
          </div>
        </div>
      </div>

      <!-- Рейтинг — завжди видимий у кутку -->
      <div
        v-if="movie.vote_average && movie.vote_average > 0"
        class="absolute top-2 left-2 flex items-center gap-0.5 bg-black/60 backdrop-blur-sm text-white text-xs font-semibold px-1.5 py-0.5 rounded-lg opacity-0 group-hover:opacity-0 transition-opacity"
        :class="{ 'opacity-100': !movie.poster_path }"
      ></div>

      <!-- Ранк бейдж (для топ-рейтингу) -->
      <div
        v-if="rank"
        class="absolute top-2 right-2 w-8 h-8 rounded-full flex items-center justify-center text-xs font-black text-white shadow-lg"
        :class="rankClass"
      >
        {{ rank }}
      </div>

      <!-- Watchlist індикатор -->
      <div
        v-if="movie.in_watchlist"
        class="absolute top-2 left-2 bg-blue-500 rounded-full p-1 shadow-md"
        title="У вашому вотчлисті"
      >
        <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
          <path d="M5 4a2 2 0 012-2h6a2 2 0 012 2v14l-5-2.5L5 18V4z"/>
        </svg>
      </div>
    </div>

    <!-- Назва і рік -->
    <div class="mt-2 px-0.5">
      <h3 class="text-sm font-semibold text-gray-900 dark:text-white line-clamp-2 leading-snug group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">
        {{ title }}
      </h3>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ year }}</p>
    </div>
  </RouterLink>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const props = defineProps({
  movie: { type: Object, required: true },
  mediaType: { type: String, default: 'movie' }, // 'movie' | 'tv'
  rank: { type: Number, default: null },
})

const title = computed(() => props.movie.title || props.movie.name || 'Без назви')
const year = computed(() => {
  const date = props.movie.release_date || props.movie.first_air_date
  return date ? date.slice(0, 4) : ''
})
const posterUrl = computed(() => {
  if (!props.movie.poster_path) return null
  return `https://image.tmdb.org/t/p/w342${props.movie.poster_path}`
})
const rankClass = computed(() => {
  if (!props.rank) return ''
  if (props.rank === 1) return 'bg-amber-400 text-gray-900'
  if (props.rank === 2) return 'bg-gray-300 text-gray-900'
  if (props.rank === 3) return 'bg-amber-700 text-white'
  return 'bg-gray-800/80 backdrop-blur-sm text-white'
})
</script>