<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="close"
      >
        <div class="absolute inset-0 bg-gray-950/85 backdrop-blur-md" />

        <Transition name="panel-swap" mode="out-in">

          <!-- ══ СТАН 1: Параметри ══ -->
          <div
            v-if="!result"
            key="params"
            class="relative z-10 w-full max-w-md bg-white dark:bg-gray-900 rounded-3xl shadow-2xl overflow-hidden border border-gray-100 dark:border-gray-800"
          >
            <div class="relative px-6 pt-6 pb-4">
              <div class="absolute inset-0 bg-gradient-to-br from-violet-500/10 via-purple-500/5 to-transparent pointer-events-none" />
              <div class="relative flex items-start justify-between">
                <div>
                  <div class="text-3xl mb-1">🎲</div>
                  <h2 class="text-xl font-black text-gray-900 dark:text-white">Випадковий вибір</h2>
                  <p class="text-sm text-gray-400 dark:text-gray-500 mt-0.5">Налаштуй — решту зроблю я</p>
                </div>
                <button @click="close" class="p-2 rounded-xl text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>

            <div class="px-6 pb-6 space-y-5">
              <!-- Тип -->
              <div>
                <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">Тип</label>
                <div class="flex gap-2">
                  <button @click="params.mediaType = 'movie'" class="flex-1 py-2.5 rounded-xl text-sm font-semibold border-2 transition-all"
                    :class="params.mediaType === 'movie' ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/20 text-violet-700 dark:text-violet-300' : 'border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400'">
                    🎬 Фільм
                  </button>
                  <button @click="params.mediaType = 'tv'" class="flex-1 py-2.5 rounded-xl text-sm font-semibold border-2 transition-all"
                    :class="params.mediaType === 'tv' ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/20 text-violet-700 dark:text-violet-300' : 'border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400'">
                    📺 Серіал
                  </button>
                </div>
              </div>

              <!-- Жанри -->
              <div>
                <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                  Жанр
                  <span v-if="params.genres.length" class="ml-1 text-violet-500 normal-case font-normal">({{ params.genres.length }} вибрано)</span>
                </label>
                <div class="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto pr-1 scrollbar-thin">
                  <button v-for="genre in genres" :key="genre.id" @click="toggleGenre(genre.id)"
                    class="px-3 py-1.5 rounded-full text-xs font-medium transition-all border"
                    :class="params.genres.includes(genre.id)
                      ? 'bg-violet-500 border-violet-500 text-white'
                      : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:border-violet-300'">
                    {{ genre.name }}
                  </button>
                </div>
              </div>

              <!-- Роки -->
              <div>
                <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                  Роки
                  <span class="ml-1 text-violet-500 normal-case font-normal">{{ params.yearFrom }} — {{ params.yearTo }}</span>
                </label>
                <div class="flex gap-3 items-center">
                  <select v-model="params.yearFrom" class="flex-1 px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400">
                    <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
                  </select>
                  <span class="text-gray-400 text-sm flex-shrink-0">до</span>
                  <select v-model="params.yearTo" class="flex-1 px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400">
                    <option v-for="y in yearOptionsTo" :key="y" :value="y">{{ y }}</option>
                  </select>
                </div>
                <div class="flex flex-wrap gap-1.5 mt-2">
                  <button v-for="preset in yearPresets" :key="preset.label" @click="applyYearPreset(preset)"
                    class="px-2.5 py-1 rounded-lg text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-violet-100 dark:hover:bg-violet-900/30 hover:text-violet-700 transition-all">
                    {{ preset.label }}
                  </button>
                </div>
              </div>

              <!-- Рейтинг -->
              <div>
                <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                  Рейтинг TMDB
                  <span class="ml-1 text-violet-500 normal-case font-normal">{{ params.minRating > 0 ? `від ${params.minRating}` : 'будь-який' }}</span>
                </label>
                <div class="flex gap-2">
                  <button v-for="r in ratingOptions" :key="r.value" @click="params.minRating = r.value"
                    class="flex-1 py-1.5 rounded-lg text-xs font-semibold border transition-all"
                    :class="params.minRating === r.value
                      ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/20 text-violet-700 dark:text-violet-300'
                      : 'border-gray-200 dark:border-gray-700 text-gray-500 hover:border-gray-300'">
                    {{ r.label }}
                  </button>
                </div>
              </div>

              <button v-if="hasCustomParams" @click="resetParams" class="w-full py-1.5 text-xs text-gray-400 hover:text-red-500 transition-colors">
                ✕ Скинути параметри
              </button>

              <button @click="findRandom" :disabled="loading"
                class="w-full py-3.5 rounded-2xl font-bold text-base transition-all"
                :class="loading ? 'bg-gray-100 dark:bg-gray-800 text-gray-400 cursor-not-allowed' : 'bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white shadow-lg hover:-translate-y-0.5 active:translate-y-0'">
                <Transition name="btn-swap" mode="out-in">
                  <span v-if="loading" key="l" class="flex items-center justify-center gap-2">
                    <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                    </svg>
                    Шукаю...
                  </span>
                  <span v-else key="i">🎲 Знайти випадковий</span>
                </Transition>
              </button>

              <Transition name="err-slide">
                <p v-if="error" class="text-center text-sm text-red-500">{{ error }}</p>
              </Transition>
            </div>
          </div>

          <!-- ══ СТАН 2: Результат ══ -->
          <div
            v-else
            key="result"
            class="relative z-10 w-full max-w-sm bg-white dark:bg-gray-900 rounded-3xl shadow-2xl overflow-hidden border border-gray-100 dark:border-gray-800"
          >
            <!-- Постер -->
            <div class="relative">
              <div class="aspect-[16/10] w-full overflow-hidden bg-gray-800">
                <!-- Backdrop якщо є, інакше постер -->
                <img
                  v-if="result.backdrop_path || result.poster_path"
                  :src="result.backdrop_path
                    ? `https://image.tmdb.org/t/p/w780${result.backdrop_path}`
                    : `https://image.tmdb.org/t/p/w500${result.poster_path}`"
                  :alt="resultTitle"
                  class="w-full h-full object-cover"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-6xl">
                  {{ params.mediaType === 'tv' ? '📺' : '🎬' }}
                </div>
              </div>

              <!-- Градієнти -->
              <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/20 to-transparent" />
              <div class="absolute inset-0 bg-gradient-to-r from-gray-900/60 to-transparent" />

              <!-- Закрити -->
              <button @click="close" class="absolute top-3 right-3 p-1.5 rounded-xl bg-black/40 text-white/70 hover:text-white hover:bg-black/60 transition-all">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>

              <!-- Постер маленький зліва + метадані -->
              <div class="absolute bottom-0 left-0 right-0 flex items-end gap-3 p-4">
                <img
                  v-if="result.poster_path"
                  :src="`https://image.tmdb.org/t/p/w185${result.poster_path}`"
                  class="w-14 rounded-lg shadow-xl flex-shrink-0 ring-1 ring-white/20"
                />
                <div class="min-w-0">
                  <div class="flex flex-wrap gap-1 mb-1">
                    <span v-if="result.vote_average" class="text-xs px-2 py-0.5 rounded-full bg-amber-400 text-gray-900 font-bold">
                      ⭐ {{ result.vote_average.toFixed(1) }}
                    </span>
                    <span v-for="genre in resultGenres" :key="genre" class="text-xs px-2 py-0.5 rounded-full bg-white/15 text-white/80 backdrop-blur-sm">
                      {{ genre }}
                    </span>
                  </div>
                  <h3 class="text-lg font-black text-white leading-tight truncate">{{ resultTitle }}</h3>
                  <p class="text-white/50 text-xs">{{ resultYear }}</p>
                </div>
              </div>
            </div>

            <!-- Опис + кнопки -->
            <div class="p-5 space-y-4">
              <p v-if="result.overview" class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed line-clamp-4">
                {{ result.overview }}
              </p>
              <p v-else class="text-sm text-gray-400 italic">Опис відсутній</p>

              <div class="flex gap-2">
                <button @click="goToResult"
                  class="flex-1 py-3 rounded-2xl font-bold text-sm bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white shadow-lg transition-all hover:-translate-y-0.5 active:translate-y-0">
                  Детальніше →
                </button>
                <button @click="findRandom" :disabled="loading"
                  class="w-14 flex-shrink-0 rounded-2xl font-bold text-lg border-2 border-gray-200 dark:border-gray-700 hover:border-violet-400 hover:text-violet-600 dark:hover:text-violet-400 transition-all disabled:opacity-40 flex items-center justify-center"
                  title="Ще раз">
                  <Transition name="btn-swap" mode="out-in">
                    <svg v-if="loading" key="s" class="animate-spin w-5 h-5 text-gray-400" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                    </svg>
                    <span v-else key="e">🎲</span>
                  </Transition>
                </button>
              </div>

              <button @click="result = null" class="w-full py-1.5 text-xs text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
                ← Змінити параметри
              </button>
            </div>
          </div>

        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { moviesAPI } from '@/services/api'

const props = defineProps({
  modelValue:       { type: Boolean, default: false },
  initialMediaType: { type: String,  default: 'movie' },
  genres:           { type: Array,   default: () => [] },
})
const emit = defineEmits(['update:modelValue'])
const router = useRouter()

const currentYear = new Date().getFullYear()

const result  = ref(null)
const loading = ref(false)
const error   = ref('')

const defaultParams = () => ({
  mediaType: props.initialMediaType,
  genres:    [],
  yearFrom:  1950,
  yearTo:    currentYear,
  minRating: 0,
})
const params = ref(defaultParams())

// ─── Computed ──────────────────────────────────────────────────
const yearOptions   = computed(() => Array.from({ length: currentYear - 1899 }, (_, i) => currentYear - i))
const yearOptionsTo = computed(() => yearOptions.value.filter(y => y >= params.value.yearFrom))
const hasCustomParams = computed(() => {
  const d = defaultParams()
  return params.value.genres.length > 0
    || params.value.yearFrom  !== d.yearFrom
    || params.value.yearTo    !== d.yearTo
    || params.value.minRating !== d.minRating
})

const resultTitle  = computed(() => result.value?.title || result.value?.name || '')
const resultYear   = computed(() => (result.value?.release_date || result.value?.first_air_date)?.slice(0, 4))
const resultGenres = computed(() => {
  if (!result.value?.genre_ids?.length || !props.genres.length) return []
  return result.value.genre_ids.slice(0, 3)
    .map(id => props.genres.find(g => g.id === id)?.name)
    .filter(Boolean)
})

const yearPresets = [
  { label: 'До 1980',   from: 1920, to: 1979 },
  { label: '80-ті',     from: 1980, to: 1989 },
  { label: '90-ті',     from: 1990, to: 1999 },
  { label: '2000-ні',   from: 2000, to: 2009 },
  { label: '2010-ні',   from: 2010, to: 2019 },
  { label: 'Свіженьке', from: 2020, to: currentYear },
]
const ratingOptions = [
  { label: 'Будь-який', value: 0 },
  { label: '5+', value: 5 },
  { label: '6+', value: 6 },
  { label: '7+', value: 7 },
  { label: '8+', value: 8 },
  { label: '9+', value: 9 },
]

// ─── Методи ────────────────────────────────────────────────────
const close = () => emit('update:modelValue', false)

const toggleGenre     = (id) => { const i = params.value.genres.indexOf(id); i === -1 ? params.value.genres.push(id) : params.value.genres.splice(i, 1) }
const applyYearPreset = (p)  => { params.value.yearFrom = p.from; params.value.yearTo = Math.min(p.to, currentYear) }
const resetParams     = ()   => { const d = defaultParams(); params.value.genres = []; params.value.yearFrom = d.yearFrom; params.value.yearTo = d.yearTo; params.value.minRating = d.minRating }

const goToResult = () => {
  if (!result.value) return
  close()
  router.push({ name: params.value.mediaType === 'tv' ? 'tv-detail' : 'movie-detail', params: { id: result.value.id } })
}

const findRandom = async () => {
  loading.value = true
  error.value   = ''

  try {
    const mediaType      = params.value.mediaType
    const discoverParams = { sort_by: 'popularity.desc' }

    if (params.value.genres.length)  discoverParams.with_genres = params.value.genres.join(',')
    if (params.value.minRating > 0) {
      discoverParams['vote_average_gte'] = params.value.minRating
      discoverParams['vote_count_gte']   = 100
    }
    if (mediaType === 'movie') {
      discoverParams['primary_release_date_gte'] = `${params.value.yearFrom}-01-01`
      discoverParams['primary_release_date_lte'] = `${params.value.yearTo}-12-31`
    } else {
      discoverParams['first_air_date_gte'] = `${params.value.yearFrom}-01-01`
      discoverParams['first_air_date_lte'] = `${params.value.yearTo}-12-31`
    }

    const firstRes   = await moviesAPI.discover({ ...discoverParams, page: 1 }, mediaType)
    const totalPages = Math.min(firstRes.data?.total_pages || 1, 20)

    if (!totalPages || firstRes.data?.total_results === 0) {
      error.value = 'Нічого не знайдено 😔 Спробуй ширші параметри'
      return
    }

    const randomPage = Math.floor(Math.random() * totalPages) + 1
    let items        = firstRes.data?.results || []

    if (randomPage > 1) {
      const pageRes = await moviesAPI.discover({ ...discoverParams, page: randomPage }, mediaType)
      items         = pageRes.data?.results || []
    }

    if (!items.length) { error.value = 'Спробуй ще раз!'; return }

    // Виключаємо поточний результат щоб не повторювався
    const pool = result.value ? items.filter(i => i.id !== result.value.id) : items
    result.value = (pool.length ? pool : items)[Math.floor(Math.random() * (pool.length || items.length))]

  } catch (e) {
    console.error(e)
    error.value = 'Помилка з\'єднання. Спробуй ще раз'
  } finally {
    loading.value = false
  }
}

watch(() => props.initialMediaType, val => { params.value.mediaType = val })
watch(params, () => { error.value = '' }, { deep: true })

const handleKey = (e) => { if (e.key === 'Escape') close() }
watch(() => props.modelValue, val => {
  if (val) document.addEventListener('keydown', handleKey)
  else     document.removeEventListener('keydown', handleKey)
})
</script>

<style scoped>
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.25s ease; }
.modal-fade-enter-from,  .modal-fade-leave-to      { opacity: 0; }

.panel-swap-enter-active { transition: all 0.35s cubic-bezier(0.34, 1.56, 0.64, 1); }
.panel-swap-leave-active { transition: all 0.2s ease; }
.panel-swap-enter-from   { opacity: 0; transform: scale(0.92) translateY(16px); }
.panel-swap-leave-to     { opacity: 0; transform: scale(0.96) translateY(8px); }

.btn-swap-enter-active, .btn-swap-leave-active { transition: all 0.15s ease; }
.btn-swap-enter-from    { opacity: 0; transform: scale(0.6); }
.btn-swap-leave-to      { opacity: 0; transform: scale(1.3); }

.err-slide-enter-active, .err-slide-leave-active { transition: all 0.25s ease; }
.err-slide-enter-from,   .err-slide-leave-to      { opacity: 0; transform: translateY(-4px); }

.scrollbar-thin { scrollbar-width: thin; scrollbar-color: #e5e7eb transparent; }
.scrollbar-thin::-webkit-scrollbar       { width: 4px; }
.scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
.scrollbar-thin::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 2px; }
</style>