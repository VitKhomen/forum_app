<template>
  <div v-if="loading" class="flex justify-center items-center py-24">
    <div class="animate-spin rounded-full h-14 w-14 border-4 border-gray-200 border-t-blue-500"></div>
  </div>

  <div v-else-if="!movie" class="text-center py-20 text-gray-500 dark:text-gray-400">
    <p class="text-5xl mb-4">🎬</p>
    <p class="text-lg">Фільм не знайдено</p>
    <RouterLink to="/" class="mt-4 inline-block text-blue-600 hover:underline">На головну</RouterLink>
  </div>

  <div v-else class="max-w-6xl mx-auto">
    <!-- Hero секція з backdrop -->
    <div class="relative rounded-2xl overflow-hidden mb-8 shadow-2xl">
      <!-- Backdrop -->
      <div
        v-if="backdropUrl"
        class="absolute inset-0 bg-cover bg-center"
        :style="{ backgroundImage: `url(${backdropUrl})` }"
      >
        <div class="absolute inset-0 bg-gradient-to-r from-black/90 via-black/60 to-black/30"></div>
        <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
      </div>
      <div v-else class="absolute inset-0 bg-gradient-to-br from-gray-900 to-gray-700"></div>

      <!-- Контент hero -->
      <div class="relative z-10 flex flex-col md:flex-row gap-8 p-6 md:p-10 min-h-[420px]">
        <!-- Постер -->
        <div class="flex-shrink-0">
          <img
            v-if="posterUrl"
            :src="posterUrl"
            :alt="movie.title"
            class="w-48 md:w-56 rounded-xl shadow-2xl ring-1 ring-white/10"
          />
          <div v-else class="w-48 md:w-56 h-72 rounded-xl bg-gray-700 flex items-center justify-center">
            <span class="text-6xl">🎬</span>
          </div>
        </div>

        <!-- Інфо -->
        <div class="flex-1 flex flex-col justify-end text-white">
          <!-- Жанри -->
          <div class="flex flex-wrap gap-2 mb-3">
            <span
              v-for="genre in movie.genres"
              :key="genre.id"
              class="text-xs px-3 py-1 rounded-full bg-white/10 backdrop-blur-sm border border-white/20 text-white/80"
            >
              {{ genre.name }}
            </span>
          </div>

          <h1 class="text-3xl md:text-4xl font-bold leading-tight mb-2">{{ movie.title }}</h1>

          <p v-if="movie.original_title && movie.original_title !== movie.title" class="text-white/50 text-sm mb-3 italic">
            {{ movie.original_title }}
          </p>

          <!-- Метадані -->
          <div class="flex flex-wrap items-center gap-4 text-sm text-white/70 mb-4">
            <span v-if="releaseYear" class="flex items-center gap-1">
              📅 {{ releaseYear }}
            </span>
            <span v-if="movie.runtime" class="flex items-center gap-1">
              ⏱ {{ formatRuntime(movie.runtime) }}
            </span>
            <span v-if="movie.vote_average" class="flex items-center gap-1 text-yellow-400 font-semibold">
              ⭐ {{ movie.vote_average.toFixed(1) }}
              <span class="text-white/40 font-normal text-xs">({{ movie.vote_count?.toLocaleString() }})</span>
            </span>
            <span v-if="movie.status" class="flex items-center gap-1">
              🎞 {{ movie.status }}
            </span>
          </div>

          <!-- Короткий опис -->
          <p class="text-white/80 text-sm leading-relaxed line-clamp-3 max-w-2xl mb-6">
            {{ movie.overview }}
          </p>

          <!-- Кнопки дій -->
          <div class="flex flex-wrap gap-3">
            <!-- Watchlist -->
            <button
              @click="toggleWatchlist"
              :disabled="actionLoading.watchlist"
              class="flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition-all duration-200"
              :class="userState.in_watchlist
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm border border-white/20'"
            >
              <span>{{ userState.in_watchlist ? '✓' : '+' }}</span>
              {{ userState.in_watchlist ? 'У списку' : 'Хочу дивитись' }}
            </button>

            <!-- Favorite -->
            <button
              @click="toggleFavorite"
              :disabled="actionLoading.favorite"
              class="flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm transition-all duration-200"
              :class="userState.is_favorite
                ? 'bg-red-600 text-white hover:bg-red-700'
                : 'bg-white/10 text-white hover:bg-white/20 backdrop-blur-sm border border-white/20'"
            >
              <span>{{ userState.is_favorite ? '❤️' : '🤍' }}</span>
              {{ userState.is_favorite ? 'Улюблений' : 'До улюблених' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Основний контент -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Лівий блок — деталі -->
      <div class="lg:col-span-2 space-y-8">

        <!-- Повний опис -->
        <div v-if="movie.overview" class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-3">Про фільм</h2>
          <p class="text-gray-700 dark:text-gray-300 leading-relaxed">{{ movie.overview }}</p>
        </div>

        <!-- Трейлер -->
        <div v-if="trailer" class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Трейлер</h2>
          <div class="aspect-video rounded-lg overflow-hidden">
            <iframe
              :src="`https://www.youtube.com/embed/${trailer.key}`"
              class="w-full h-full"
              frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
            ></iframe>
          </div>
        </div>

        <!-- Акторський склад -->
        <div v-if="cast.length" class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">У головних ролях</h2>
          <div class="flex gap-4 overflow-x-auto pb-2 scrollbar-thin">
            <div
              v-for="actor in cast"
              :key="actor.id"
              class="flex-shrink-0 w-24 text-center"
            >
              <div class="w-24 h-24 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-700 mb-2 mx-auto">
                <img
                  v-if="actor.profile_path"
                  :src="`https://image.tmdb.org/t/p/w185${actor.profile_path}`"
                  :alt="actor.name"
                  class="w-full h-full object-cover"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-3xl">👤</div>
              </div>
              <p class="text-xs font-medium text-gray-900 dark:text-white line-clamp-2 leading-tight">{{ actor.name }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 line-clamp-1 mt-0.5">{{ actor.character }}</p>
            </div>
          </div>
        </div>

        <!-- Схожі фільми -->
        <div v-if="similar.length" class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Схожі фільми</h2>
          <div class="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <RouterLink
              v-for="film in similar"
              :key="film.id"
              :to="`/movies/${film.id}`"
              class="group"
            >
              <div class="aspect-[2/3] rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700 mb-2">
                <img
                  v-if="film.poster_path"
                  :src="`https://image.tmdb.org/t/p/w342${film.poster_path}`"
                  :alt="film.title"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-4xl">🎬</div>
              </div>
              <p class="text-sm font-medium text-gray-900 dark:text-white line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                {{ film.title }}
              </p>
              <p v-if="film.release_date" class="text-xs text-gray-500 mt-0.5">
                {{ film.release_date.slice(0, 4) }}
              </p>
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- Правий блок — сайдбар -->
      <div class="space-y-6">

        <!-- Оцінка юзера -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Моя оцінка</h3>

          <div v-if="!isAuthenticated" class="text-sm text-gray-500 dark:text-gray-400 text-center py-2">
            <RouterLink to="/login" class="text-blue-600 hover:underline">Увійдіть</RouterLink>, щоб оцінити
          </div>

          <div v-else>
            <!-- Зірки -->
            <div class="flex gap-1 mb-3 justify-center">
              <button
                v-for="n in 10"
                :key="n"
                @click="setRating(n)"
                class="text-2xl transition-transform hover:scale-110"
                :class="n <= (hoverRating || userState.user_rating) ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'"
                @mouseenter="hoverRating = n"
                @mouseleave="hoverRating = 0"
              >
                ★
              </button>
            </div>

            <p class="text-center text-sm text-gray-600 dark:text-gray-400 mb-3">
              <span v-if="userState.user_rating">Ваша оцінка: <span class="font-bold text-yellow-500">{{ userState.user_rating }}/10</span></span>
              <span v-else>Клікніть щоб оцінити</span>
            </p>

            <button
              v-if="userState.user_rating"
              @click="deleteRating"
              :disabled="actionLoading.rating"
              class="w-full text-xs text-red-500 hover:text-red-700 transition-colors"
            >
              Видалити оцінку
            </button>
          </div>
        </div>

        <!-- Деталі -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-6 space-y-3">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">Деталі</h3>

          <div v-if="movie.release_date" class="flex justify-between text-sm">
            <span class="text-gray-500 dark:text-gray-400">Дата виходу</span>
            <span class="text-gray-900 dark:text-white font-medium">{{ formatDate(movie.release_date) }}</span>
          </div>

          <div v-if="movie.budget" class="flex justify-between text-sm">
            <span class="text-gray-500 dark:text-gray-400">Бюджет</span>
            <span class="text-gray-900 dark:text-white font-medium">${{ formatMoney(movie.budget) }}</span>
          </div>

          <div v-if="movie.revenue" class="flex justify-between text-sm">
            <span class="text-gray-500 dark:text-gray-400">Касові збори</span>
            <span class="text-gray-900 dark:text-white font-medium">${{ formatMoney(movie.revenue) }}</span>
          </div>

          <div v-if="movie.production_countries?.length" class="flex justify-between text-sm">
            <span class="text-gray-500 dark:text-gray-400">Країна</span>
            <span class="text-gray-900 dark:text-white font-medium">
              {{ movie.production_countries.map(c => c.name).join(', ') }}
            </span>
          </div>

          <div v-if="movie.spoken_languages?.length" class="flex justify-between text-sm">
            <span class="text-gray-500 dark:text-gray-400">Мова</span>
            <span class="text-gray-900 dark:text-white font-medium">
              {{ movie.spoken_languages.map(l => l.name).join(', ') }}
            </span>
          </div>
        </div>

        <!-- Режисер -->
        <div v-if="director" class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-3">Режисер</h3>
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-700 flex-shrink-0">
              <img
                v-if="director.profile_path"
                :src="`https://image.tmdb.org/t/p/w185${director.profile_path}`"
                :alt="director.name"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-xl">🎬</div>
            </div>
            <p class="text-sm font-medium text-gray-900 dark:text-white">{{ director.name }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { moviesAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const route = useRoute()
const authStore = useAuthStore()
const toast = useToast()

const movie = ref(null)
const loading = ref(true)
const hoverRating = ref(0)

const userState = ref({
  in_watchlist: false,
  is_favorite: false,
  user_rating: null,
})

const actionLoading = ref({
  watchlist: false,
  favorite: false,
  rating: false,
})

const isAuthenticated = computed(() => authStore.isAuthenticated)

// Зображення
const posterUrl = computed(() => {
  if (!movie.value?.poster_path) return null
  return `https://image.tmdb.org/t/p/w500${movie.value.poster_path}`
})

const backdropUrl = computed(() => {
  if (!movie.value?.backdrop_path) return null
  return `https://image.tmdb.org/t/p/w1280${movie.value.backdrop_path}`
})

// Рік
const releaseYear = computed(() => {
  return movie.value?.release_date?.slice(0, 4)
})

// Трейлер
const trailer = computed(() => {
  const videos = movie.value?.videos?.results || []
  return videos.find(v => v.type === 'Trailer' && v.site === 'YouTube') || null
})

// Акторський склад (перші 10)
const cast = computed(() => {
  return (movie.value?.credits?.cast || []).slice(0, 10)
})

// Режисер
const director = computed(() => {
  return (movie.value?.credits?.crew || []).find(p => p.job === 'Director') || null
})

// Схожі фільми (перші 6)
const similar = computed(() => {
  return (movie.value?.similar?.results || []).slice(0, 6)
})

// Форматування
const formatRuntime = (mins) => {
  const h = Math.floor(mins / 60)
  const m = mins % 60
  return h ? `${h}г ${m}хв` : `${m}хв`
}

const formatDate = (str) => {
  if (!str) return ''
  const d = new Date(str)
  return d.toLocaleDateString('uk-UA', { day: 'numeric', month: 'long', year: 'numeric' })
}

const formatMoney = (n) => {
  if (!n) return '—'
  if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B'
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M'
  return n.toLocaleString()
}

// Дії
const toggleWatchlist = async () => {
  if (!isAuthenticated.value) { toast.warning('Увійдіть щоб додати до списку'); return }
  actionLoading.value.watchlist = true
  try {
    if (userState.value.in_watchlist) {
      await moviesAPI.removeWatchlist(route.params.id)
      userState.value.in_watchlist = false
      toast.success('Видалено зі списку')
    } else {
      await moviesAPI.toggleWatchlist(route.params.id)
      userState.value.in_watchlist = true
      toast.success('Додано до списку')
    }
  } catch (e) {
    toast.error('Помилка')
  } finally {
    actionLoading.value.watchlist = false
  }
}

const toggleFavorite = async () => {
  if (!isAuthenticated.value) { toast.warning('Увійдіть щоб додати до улюблених'); return }
  actionLoading.value.favorite = true
  try {
    if (userState.value.is_favorite) {
      await moviesAPI.removeFavorite(route.params.id)
      userState.value.is_favorite = false
      toast.success('Видалено з улюблених')
    } else {
      await moviesAPI.toggleFavorite(route.params.id)
      userState.value.is_favorite = true
      toast.success('Додано до улюблених')
    }
  } catch (e) {
    toast.error('Помилка')
  } finally {
    actionLoading.value.favorite = false
  }
}

const setRating = async (rating) => {
  if (!isAuthenticated.value) return
  actionLoading.value.rating = true
  try {
    if (userState.value.user_rating) {
      await moviesAPI.updateRating(route.params.id, rating)
    } else {
      await moviesAPI.rateMovie(route.params.id, rating)
    }
    userState.value.user_rating = rating
    toast.success(`Оцінка ${rating}/10 збережена`)
  } catch (e) {
    toast.error('Помилка збереження оцінки')
  } finally {
    actionLoading.value.rating = false
  }
}

const deleteRating = async () => {
  actionLoading.value.rating = true
  try {
    await moviesAPI.deleteRating(route.params.id)
    userState.value.user_rating = null
    toast.success('Оцінку видалено')
  } catch (e) {
    toast.error('Помилка')
  } finally {
    actionLoading.value.rating = false
  }
}

const fetchMovie = async () => {
  loading.value = true
  try {
    const { data } = await moviesAPI.getById(route.params.id)
    movie.value = data
    userState.value = {
      in_watchlist: data.user_state?.in_watchlist || false,
      is_favorite: data.user_state?.is_favorite || false,
      user_rating: data.user_state?.user_rating || null,
    }
  } catch (e) {
    movie.value = null
  } finally {
    loading.value = false
  }
}

// Перезавантажуємо при зміні роуту (схожі фільми)
watch(() => route.params.id, fetchMovie)
onMounted(fetchMovie)
</script>