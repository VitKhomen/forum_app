<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-950">

    <!-- ══════════════════════════════════════════════════
         HERO SECTION — показується коли немає активного пошуку/фільтрів
    ══════════════════════════════════════════════════ -->
    <Transition name="hero-slide">
      <section
        v-if="mode === 'home'"
        class="relative -mx-4 sm:-mx-6 lg:-mx-8 -mt-6 mb-10 h-[460px] overflow-hidden"
      >
        <!-- Динамічний backdrop -->
        <Transition name="bg-fade" mode="out-in">
          <div
            :key="heroIndex"
            class="absolute inset-0 bg-cover bg-center"
            :style="heroItem?.backdrop_path
              ? { backgroundImage: `url(https://image.tmdb.org/t/p/w1280${heroItem.backdrop_path})` }
              : { background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)' }"
          />
        </Transition>
        <!-- Градієнт поверх -->
        <div class="absolute inset-0 bg-gradient-to-r from-gray-950/95 via-gray-950/70 to-transparent" />
        <div class="absolute inset-0 bg-gradient-to-t from-gray-950/80 via-transparent to-transparent" />

        <!-- Контент hero -->
        <div class="relative z-10 h-full flex items-end px-4 sm:px-6 lg:px-8 pb-10">
          <div class="max-w-xl">
            <!-- Перемикач тип медіа -->
            <div class="flex mb-6">
              <div class="inline-flex bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-1 gap-1">
                <button
                  @click="switchMediaType('movie')"
                  class="px-5 py-2 rounded-xl text-sm font-semibold transition-all duration-300"
                  :class="mediaType === 'movie'
                    ? 'bg-amber-400 text-gray-900 shadow-lg'
                    : 'text-white/70 hover:text-white'"
                >
                  🎬 Фільми
                </button>
                <button
                  @click="switchMediaType('tv')"
                  class="px-5 py-2 rounded-xl text-sm font-semibold transition-all duration-300"
                  :class="mediaType === 'tv'
                    ? 'bg-amber-400 text-gray-900 shadow-lg'
                    : 'text-white/70 hover:text-white'"
                >
                  📺 Серіали
                </button>
              </div>
            </div>

            <!-- Заголовок з поточним топ-фільмом -->
            <Transition name="text-slide" mode="out-in">
              <div :key="heroIndex">
                <p class="text-amber-400 text-sm font-semibold uppercase tracking-widest mb-2">
                  🔥 Топ тижня
                </p>
                <h2 class="text-3xl sm:text-4xl font-black text-white mb-3 leading-tight">
                  {{ heroTitle }}
                </h2>
                <p v-if="heroItem?.overview" class="text-white/60 text-sm leading-relaxed line-clamp-2 mb-5">
                  {{ heroItem.overview }}
                </p>
              </div>
            </Transition>

            <!-- Пошук в hero -->
            <div class="relative max-w-lg">
              <input
                v-model="searchQuery"
                @keyup.enter="applySearch"
                type="search"
                :placeholder="mediaType === 'movie' ? 'Знайти фільм...' : 'Знайти серіал...'"
                class="w-full px-5 py-3.5 pr-14 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20 text-white placeholder-white/40 focus:outline-none focus:bg-white/15 focus:border-amber-400/50 transition-all text-sm"
              />
              <button
                @click="applySearch"
                class="absolute right-2 top-2 bottom-2 px-4 bg-amber-400 hover:bg-amber-300 text-gray-900 rounded-xl font-bold text-sm transition-colors"
              >
                →
              </button>
            </div>

            <!-- Dots навігація hero -->
            <div class="flex gap-2 mt-5">
              <button
                v-for="(_, i) in trendingItems.slice(0, 5)"
                :key="i"
                @click="heroIndex = i"
                class="h-1.5 rounded-full transition-all duration-300"
                :class="heroIndex === i ? 'w-8 bg-amber-400' : 'w-1.5 bg-white/30 hover:bg-white/50'"
              />
            </div>
          </div>
        </div>

        <!-- Постери праворуч -->
        <div class="absolute right-0 top-0 bottom-0 w-1/3 hidden lg:flex items-center justify-end pr-8 gap-3 overflow-hidden">
          <TransitionGroup name="poster-cascade">
            <div
              v-for="(item, i) in trendingItems.slice(heroIndex + 1, heroIndex + 4)"
              :key="item.id"
              class="relative flex-shrink-0 rounded-xl overflow-hidden shadow-2xl"
              :class="i === 0 ? 'w-32 h-48 opacity-90' : i === 1 ? 'w-28 h-40 opacity-60' : 'w-24 h-32 opacity-30'"
            >
              <img
                v-if="item.poster_path"
                :src="`https://image.tmdb.org/t/p/w185${item.poster_path}`"
                class="w-full h-full object-cover"
              />
            </div>
          </TransitionGroup>
        </div>
      </section>
    </Transition>

    <!-- ══════════════════════════════════════════════════
         ПАНЕЛЬ ФІЛЬТРІВ (завжди видима)
    ══════════════════════════════════════════════════ -->
    <div class="sticky top-0 z-30 -mx-4 sm:-mx-6 lg:-mx-8 px-4 sm:px-6 lg:px-8 py-3 bg-white/95 dark:bg-gray-950/95 backdrop-blur-xl border-b border-gray-200 dark:border-gray-800 mb-6 shadow-sm">
      <div class="flex flex-wrap items-center gap-2">

        <!-- Тип медіа (компактний, якщо не hero режим) -->
        <div v-if="mode !== 'home'" class="flex bg-gray-100 dark:bg-gray-800 rounded-xl p-0.5 gap-0.5 flex-shrink-0">
          <button
            @click="switchMediaType('movie')"
            class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all"
            :class="mediaType === 'movie' ? 'bg-white dark:bg-gray-700 shadow text-gray-900 dark:text-white' : 'text-gray-400'"
          >🎬 Фільми</button>
          <button
            @click="switchMediaType('tv')"
            class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all"
            :class="mediaType === 'tv' ? 'bg-white dark:bg-gray-700 shadow text-gray-900 dark:text-white' : 'text-gray-400'"
          >📺 Серіали</button>
        </div>

        <!-- Жанри -->
        <select
          v-model="selectedGenre"
          @change="applyFilters"
          class="px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-amber-400 cursor-pointer"
        >
          <option value="">Всі жанри</option>
          <option v-for="g in genres" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>

        <!-- Рік -->
        <select
          v-model="selectedYear"
          @change="applyFilters"
          class="px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-amber-400 cursor-pointer"
        >
          <option value="">Будь-який рік</option>
          <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
        </select>

        <!-- Сортування -->
        <select
          v-model="sortBy"
          @change="applyFilters"
          class="px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-amber-400 cursor-pointer"
        >
          <option value="popularity.desc">🔥 Популярні</option>
          <option value="vote_average.desc">⭐ Рейтинг</option>
          <option value="release_date.desc">🆕 Нові</option>
          <option value="revenue.desc">💰 Касові</option>
          <option value="vote_count.desc">💬 Найбільше оцінок</option>
        </select>

        <!-- Пошук (якщо не hero) -->
        <div v-if="mode !== 'home'" class="flex-1 min-w-0 max-w-sm relative">
          <input
            v-model="searchQuery"
            @keyup.enter="applySearch"
            type="search"
            placeholder="Пошук..."
            class="w-full px-4 py-2 pr-10 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs focus:outline-none focus:ring-2 focus:ring-amber-400"
          />
          <button
            v-if="searchQuery"
            @click="clearSearch"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
          >✕</button>
        </div>

        <!-- Рандом -->
        <button
          @click="openRandom"
          :disabled="loadingRandom"
          class="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white rounded-xl text-xs font-semibold transition-all shadow-md disabled:opacity-50 flex-shrink-0"
        >
          <span :class="{ 'inline-block animate-spin': loadingRandom }">🎲</span>
          Рандом
        </button>

        <!-- Очистити фільтри -->
        <button
          v-if="hasActiveFilters"
          @click="clearAllFilters"
          class="px-3 py-2 text-xs text-red-500 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-colors flex-shrink-0"
        >
          ✕ Очистити
        </button>

        <!-- Активний пошук чіп -->
        <span
          v-if="activeSearch"
          class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-amber-100 dark:bg-amber-900/40 text-amber-800 dark:text-amber-300 rounded-full text-xs font-medium"
        >
          🔍 "{{ activeSearch }}"
          <button @click="clearSearch" class="hover:text-amber-900 dark:hover:text-amber-100 ml-0.5">✕</button>
        </span>

        <!-- Вигляд -->
        <div class="ml-auto flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5">
          <button
            @click="viewMode = 'grid'"
            :class="viewMode === 'grid' ? 'bg-white dark:bg-gray-700 shadow' : 'text-gray-400'"
            class="p-1.5 rounded-md transition-all"
            title="Сітка"
          >
            <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 16 16">
              <path d="M1 2.5A1.5 1.5 0 012.5 1h3A1.5 1.5 0 017 2.5v3A1.5 1.5 0 015.5 7h-3A1.5 1.5 0 011 5.5zm8 0A1.5 1.5 0 0110.5 1h3A1.5 1.5 0 0115 2.5v3A1.5 1.5 0 0113.5 7h-3A1.5 1.5 0 019 5.5zm-8 8A1.5 1.5 0 012.5 9h3A1.5 1.5 0 017 10.5v3A1.5 1.5 0 015.5 15h-3A1.5 1.5 0 011 13.5zm8 0A1.5 1.5 0 0110.5 9h3A1.5 1.5 0 0115 10.5v3A1.5 1.5 0 0113.5 15h-3A1.5 1.5 0 019 13.5z"/>
            </svg>
          </button>
          <button
            @click="viewMode = 'list'"
            :class="viewMode === 'list' ? 'bg-white dark:bg-gray-700 shadow' : 'text-gray-400'"
            class="p-1.5 rounded-md transition-all"
            title="Список"
          >
            <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 16 16">
              <path fill-rule="evenodd" d="M2.5 12a.5.5 0 01.5-.5h10a.5.5 0 010 1H3a.5.5 0 01-.5-.5zm0-4a.5.5 0 01.5-.5h10a.5.5 0 010 1H3a.5.5 0 01-.5-.5zm0-4a.5.5 0 01.5-.5h10a.5.5 0 010 1H3a.5.5 0 01-.5-.5z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════════════
         HOME MODE — секції без пошуку
    ══════════════════════════════════════════════════ -->
    <template v-if="mode === 'home'">

      <!-- Трендові -->
      <MovieSection
        title="🔥 Топ тижня"
        :items="trendingItems.slice(0, 10)"
        :media-type="mediaType"
        :loading="sectionsLoading"
        @see-all="browseTrending"
      />

      <!-- Зараз в кіно / На ефірі -->
      <MovieSection
        :title="mediaType === 'movie' ? '🎭 Зараз в кіно' : '📡 На ефірі'"
        :items="nowPlayingItems"
        :media-type="mediaType"
        :loading="sectionsLoading"
        @see-all="browseCategory(mediaType === 'movie' ? 'now_playing' : 'on_the_air')"
      />

      <!-- Топ рейтинг -->
      <MovieSection
        title="⭐ Найвищий рейтинг"
        :items="topRatedItems.slice(0, 10)"
        :media-type="mediaType"
        :loading="sectionsLoading"
        :show-rank="true"
        @see-all="browseCategory('top_rated')"
      />

      <!-- Рекомендації (для авторизованих) -->
      <MovieSection
        v-if="isAuthenticated && recommendations.length"
        title="💡 Для вас — на основі вотчлиста"
        :items="recommendations"
        :media-type="mediaType"
        @see-all="null"
      />

    </template>

    <!-- ══════════════════════════════════════════════════
         BROWSE / SEARCH MODE — сітка або список
    ══════════════════════════════════════════════════ -->
    <template v-else>

      <!-- Спінер -->
      <div v-if="loading" class="flex justify-center py-24">
        <div class="flex flex-col items-center gap-3">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-gray-200 dark:border-gray-700 border-t-amber-400"></div>
          <p class="text-sm text-gray-400">Завантаження...</p>
        </div>
      </div>

      <template v-else-if="results.length">
        <!-- Info рядок -->
        <div class="flex items-center justify-between mb-4">
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Знайдено <span class="font-semibold text-gray-900 dark:text-white">{{ totalResults.toLocaleString() }}</span>
          </p>
        </div>

        <!-- Grid -->
        <div
          v-if="viewMode === 'grid'"
          class="grid grid-cols-2 xs:grid-cols-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4 mb-8"
        >
          <MovieCard
            v-for="(item, i) in results"
            :key="item.id"
            :movie="item"
            :media-type="mediaType"
            class="animate-fade-in"
            :style="{ animationDelay: `${i * 30}ms` }"
          />
        </div>

        <!-- List -->
        <div v-else class="space-y-2 mb-8">
          <RouterLink
            v-for="item in results"
            :key="item.id"
            :to="{ name: mediaType === 'movie' ? 'movie-detail' : 'tv-detail', params: { id: item.id } }"
            class="flex gap-4 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-xl p-3 hover:shadow-md hover:border-amber-400/30 transition-all group"
          >
            <div class="w-12 flex-shrink-0 aspect-[2/3] rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
              <img
                v-if="item.poster_path"
                :src="`https://image.tmdb.org/t/p/w92${item.poster_path}`"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-gray-300 dark:text-gray-600 text-xl">🎬</div>
            </div>
            <div class="flex-1 min-w-0 py-0.5">
              <div class="flex items-start justify-between gap-2">
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors line-clamp-1">
                  {{ item.title || item.name }}
                </h3>
                <div v-if="item.vote_average" class="flex items-center gap-0.5 text-amber-500 text-xs font-bold flex-shrink-0">
                  <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                  {{ item.vote_average.toFixed(1) }}
                </div>
              </div>
              <p class="text-xs text-gray-400 mt-0.5">{{ (item.release_date || item.first_air_date)?.slice(0, 4) }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2 leading-relaxed">{{ item.overview }}</p>
            </div>
          </RouterLink>
        </div>

        <!-- Пагінація -->
        <nav class="flex justify-center items-center gap-1.5 flex-wrap pb-8">
          <button
            :disabled="currentPage <= 1"
            @click="goToPage(currentPage - 1)"
            class="px-4 py-2 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            ← Назад
          </button>

          <template v-for="p in visiblePages" :key="p">
            <span v-if="p === '...'" class="px-2 text-gray-400 text-sm">…</span>
            <button
              v-else
              @click="goToPage(p)"
              class="w-10 h-10 rounded-xl text-sm font-medium transition-all"
              :class="currentPage === p
                ? 'bg-amber-400 text-gray-900 font-bold shadow-md'
                : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'"
            >
              {{ p }}
            </button>
          </template>

          <button
            :disabled="currentPage >= totalPages"
            @click="goToPage(currentPage + 1)"
            class="px-4 py-2 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
          >
            Далі →
          </button>
        </nav>
      </template>

      <!-- Порожньо -->
      <div v-else-if="!loading" class="flex flex-col items-center py-24 text-gray-400 dark:text-gray-600">
        <svg class="w-16 h-16 mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <p class="text-lg font-medium">Нічого не знайдено</p>
        <p class="text-sm mt-1">Спробуйте інший запит або змініть фільтри</p>
        <button @click="clearAllFilters" class="mt-4 px-5 py-2 bg-amber-400 text-gray-900 rounded-xl text-sm font-semibold hover:bg-amber-300 transition-colors">
          Скинути фільтри
        </button>
      </div>

    </template>

  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth' // або твій auth store
import { moviesAPI } from '@/services/api'
import MovieCard from '@/components/movies/MovieCard.vue'
import MovieSection from '@/components/movies/MovieSection.vue'

const route = useRoute()
const router = useRouter()

// Якщо немає auth store — замінити на свій
let isAuthenticated = ref(false)
try {
  const authStore = useAuthStore()
  isAuthenticated = computed(() => authStore.isAuthenticated)
} catch {}

// ─── Стан ──────────────────────────────────────────────────────────────
const mediaType   = ref('movie')   // 'movie' | 'tv'
const searchQuery = ref('')
const activeSearch = ref('')
const selectedGenre = ref('')
const selectedYear  = ref('')
const sortBy        = ref('popularity.desc')
const viewMode      = ref('grid')
const currentPage   = ref(1)

// mode: 'home' | 'browse' | 'search'
const mode = computed(() => {
  if (activeSearch.value) return 'search'
  if (selectedGenre.value || selectedYear.value || sortBy.value !== 'popularity.desc') return 'browse'
  return 'home'
})

const loading = ref(false)
const sectionsLoading = ref(false)
const loadingRandom   = ref(false)

const results      = ref([])
const totalResults = ref(0)
const totalPages   = ref(0)

// Секції для home
const trendingItems   = ref([])
const nowPlayingItems = ref([])
const topRatedItems   = ref([])
const recommendations = ref([])
const genres          = ref([])

// Hero carousel
const heroIndex = ref(0)
let heroTimer = null
const heroItem  = computed(() => trendingItems.value[heroIndex.value] || null)
const heroTitle = computed(() => heroItem.value?.title || heroItem.value?.name || 'Кінотека')

// ─── Computed ──────────────────────────────────────────────────────────
const hasActiveFilters = computed(() =>
  !!activeSearch.value || !!selectedGenre.value || !!selectedYear.value || sortBy.value !== 'popularity.desc'
)

const yearOptions = computed(() => {
  const cur = new Date().getFullYear()
  return Array.from({ length: cur - 1899 }, (_, i) => cur - i)
})

const visiblePages = computed(() => {
  const total = Math.min(totalPages.value, 20)
  const cur   = currentPage.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)
  const pages = [1]
  if (cur > 3) pages.push('...')
  for (let i = Math.max(2, cur - 1); i <= Math.min(total - 1, cur + 1); i++) pages.push(i)
  if (cur < total - 2) pages.push('...')
  pages.push(total)
  return pages
})

// ─── Методи ────────────────────────────────────────────────────────────
const fetchResults = async () => {
  loading.value = true
  try {
    let data
    if (activeSearch.value) {
      const res = await moviesAPI.search(activeSearch.value, currentPage.value, mediaType.value)
      data = res.data
    } else {
      const params = {
        sort_by: sortBy.value,
        page: currentPage.value,
      }
      if (selectedGenre.value) params.with_genres = selectedGenre.value
      if (selectedYear.value) {
        params[mediaType.value === 'movie' ? 'primary_release_year' : 'first_air_date_year'] = selectedYear.value
      }
      const res = await moviesAPI.discover(params, mediaType.value)
      data = res.data
    }
    results.value = data?.results || []
    totalResults.value = data?.total_results || 0
    totalPages.value = Math.min(data?.total_pages || 1, 20)
  } catch (err) {
    console.error('fetchResults:', err)
    results.value = []
  } finally {
    loading.value = false
  }
}

const fetchHomeSections = async () => {
  sectionsLoading.value = true
  try {
    const type = mediaType.value
    const [trending, nowPlaying, topRated] = await Promise.allSettled([
      moviesAPI.trending(type),
      moviesAPI.nowPlaying(type),
      moviesAPI.topRated(type),
    ])
    trendingItems.value   = trending.value?.data?.results || []
    nowPlayingItems.value = nowPlaying.value?.data?.results || []
    topRatedItems.value   = topRated.value?.data?.results || []
  } catch (err) {
    console.error('fetchHomeSections:', err)
  } finally {
    sectionsLoading.value = false
  }
}

const fetchGenres = async () => {
  try {
    const res = await moviesAPI.genres(mediaType.value)
    genres.value = res.data?.genres || []
  } catch {}
}

const fetchRecommendations = async () => {
  if (!isAuthenticated.value) return
  try {
    // Беремо перший фільм з вотчлиста і просимо рекомендації
    const wlRes = await moviesAPI.getMyWatchlist()
    const wl = wlRes.data?.results || []
    if (wl.length) {
      const res = await moviesAPI.recommendations(wl[0].tmdb_id, mediaType.value)
      recommendations.value = res.data?.results?.slice(0, 10) || []
    }
  } catch {}
}

// ─── Search / Filters ──────────────────────────────────────────────────
const applySearch = () => {
  if (!searchQuery.value.trim()) return
  activeSearch.value = searchQuery.value.trim()
  currentPage.value  = 1
  syncURL()
  fetchResults()
}

const applyFilters = () => {
  currentPage.value = 1
  syncURL()
  if (mode.value !== 'home') fetchResults()
  else fetchResults()
}

const clearSearch = () => {
  searchQuery.value = ''
  activeSearch.value = ''
  currentPage.value  = 1
  syncURL()
  if (!hasActiveFilters.value) return
  fetchResults()
}

const clearAllFilters = () => {
  searchQuery.value  = ''
  activeSearch.value = ''
  selectedGenre.value = ''
  selectedYear.value  = ''
  sortBy.value        = 'popularity.desc'
  currentPage.value   = 1
  router.replace({ query: {} })
}

const goToPage = (p) => {
  if (p < 1 || p > totalPages.value) return
  currentPage.value = p
  syncURL()
  fetchResults()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const switchMediaType = (type) => {
  if (mediaType.value === type) return
  mediaType.value = type
  currentPage.value = 1
  results.value = []
  Promise.all([fetchGenres(), fetchHomeSections()])
  if (mode.value !== 'home') fetchResults()
  if (isAuthenticated.value) fetchRecommendations()
}

const browseCategory = (cat) => {
  sortBy.value = cat === 'top_rated' ? 'vote_average.desc' : 'popularity.desc'
  currentPage.value = 1
  syncURL()
  fetchResults()
}

const browseTrending = () => {
  sortBy.value = 'popularity.desc'
  currentPage.value = 1
  syncURL()
  fetchResults()
}

const openRandom = async () => {
  loadingRandom.value = true
  try {
    const randomPage = Math.floor(Math.random() * 50) + 1
    const res = await moviesAPI.discover({ sort_by: 'popularity.desc', page: randomPage }, mediaType.value)
    const items = res.data?.results || []
    if (items.length) {
      const item = items[Math.floor(Math.random() * items.length)]
      const routeName = mediaType.value === 'movie' ? 'movie-detail' : 'tv-detail'
      router.push({ name: routeName, params: { id: item.id } })
    }
  } catch (e) {
    console.error(e)
  } finally {
    loadingRandom.value = false
  }
}

// ─── URL sync ──────────────────────────────────────────────────────────
const syncURL = () => {
  const q = {}
  if (activeSearch.value) q.q = activeSearch.value
  if (selectedGenre.value) q.genre = selectedGenre.value
  if (selectedYear.value) q.year = selectedYear.value
  if (sortBy.value !== 'popularity.desc') q.sort = sortBy.value
  if (mediaType.value !== 'movie') q.type = mediaType.value
  if (currentPage.value > 1) q.page = currentPage.value
  router.replace({ query: q })
}

const loadFromURL = () => {
  const q = route.query
  if (q.q)     { searchQuery.value = q.q; activeSearch.value = q.q }
  if (q.genre)  selectedGenre.value = q.genre
  if (q.year)   selectedYear.value  = q.year
  if (q.sort)   sortBy.value        = q.sort
  if (q.type)   mediaType.value     = q.type
  if (q.page)   currentPage.value   = Number(q.page)
}

// ─── Hero автопрокрутка ────────────────────────────────────────────────
const startHeroTimer = () => {
  heroTimer = setInterval(() => {
    heroIndex.value = (heroIndex.value + 1) % Math.min(trendingItems.value.length, 5)
  }, 5000)
}

watch(trendingItems, (val) => {
  if (val.length && !heroTimer) startHeroTimer()
})

// ─── Lifecycle ────────────────────────────────────────────────────────
onMounted(async () => {
  loadFromURL()
  await Promise.all([fetchGenres(), fetchHomeSections()])
  if (hasActiveFilters.value) fetchResults()
  if (isAuthenticated.value) fetchRecommendations()
})
</script>

<style scoped>
/* Hero transitions */
.hero-slide-enter-active,
.hero-slide-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.hero-slide-enter-from,
.hero-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Backdrop fade */
.bg-fade-enter-active,
.bg-fade-leave-active {
  transition: opacity 1.5s ease;
}
.bg-fade-enter-from,
.bg-fade-leave-to {
  opacity: 0;
}

/* Text slide */
.text-slide-enter-active,
.text-slide-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.text-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.text-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Poster cascade */
.poster-cascade-enter-active {
  transition: all 0.5s ease;
}
.poster-cascade-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

/* Card fade in */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
  animation: fadeIn 0.4s ease both;
}
</style>