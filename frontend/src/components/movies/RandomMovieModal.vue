<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @click.self="$emit('update:modelValue', false)"
      >
        <!-- Blur backdrop -->
        <div class="absolute inset-0 bg-gray-950/80 backdrop-blur-sm" />

        <!-- Панель -->
        <Transition name="modal-scale">
          <div
            v-if="modelValue"
            class="relative z-10 w-full max-w-md bg-white dark:bg-gray-900 rounded-3xl shadow-2xl overflow-hidden border border-gray-100 dark:border-gray-800"
          >
            <!-- Header -->
            <div class="relative px-6 pt-6 pb-4">
              <!-- Декоративний градієнт -->
              <div class="absolute inset-0 bg-gradient-to-br from-violet-500/10 via-purple-500/5 to-transparent pointer-events-none" />

              <div class="relative flex items-start justify-between">
                <div>
                  <div class="text-3xl mb-1">🎲</div>
                  <h2 class="text-xl font-black text-gray-900 dark:text-white">Випадковий фільм</h2>
                  <p class="text-sm text-gray-400 dark:text-gray-500 mt-0.5">Налаштуй параметри — решту зроблю я</p>
                </div>
                <button
                  @click="$emit('update:modelValue', false)"
                  class="p-2 rounded-xl text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>

            <!-- Body -->
            <div class="px-6 pb-6 space-y-5">

              <!-- Тип -->
              <div>
                <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                  Тип
                </label>
                <div class="flex gap-2">
                  <button
                    @click="params.mediaType = 'movie'"
                    class="flex-1 py-2.5 rounded-xl text-sm font-semibold border-2 transition-all"
                    :class="params.mediaType === 'movie'
                      ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/20 text-violet-700 dark:text-violet-300'
                      : 'border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:border-gray-300'"
                  >
                    🎬 Фільм
                  </button>
                  <button
                    @click="params.mediaType = 'tv'"
                    class="flex-1 py-2.5 rounded-xl text-sm font-semibold border-2 transition-all"
                    :class="params.mediaType === 'tv'
                      ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/20 text-violet-700 dark:text-violet-300'
                      : 'border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400 hover:border-gray-300'"
                  >
                    📺 Серіал
                  </button>
                </div>
              </div>

              <!-- Жанри -->
              <div>
                <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                  Жанр
                  <span v-if="params.genres.length" class="ml-1 text-violet-500 normal-case font-normal">
                    ({{ params.genres.length }} вибрано)
                  </span>
                </label>
                <div class="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto pr-1 scrollbar-thin">
                  <button
                    v-for="genre in genres"
                    :key="genre.id"
                    @click="toggleGenre(genre.id)"
                    class="px-3 py-1.5 rounded-full text-xs font-medium transition-all border"
                    :class="params.genres.includes(genre.id)
                      ? 'bg-violet-500 border-violet-500 text-white shadow-md shadow-violet-200 dark:shadow-violet-900/30'
                      : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:border-violet-300 dark:hover:border-violet-600'"
                  >
                    {{ genre.name }}
                  </button>
                </div>
              </div>

              <!-- Діапазон років -->
              <div>
                <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                  Роки випуску
                  <span class="ml-1 text-violet-500 normal-case font-normal">
                    {{ params.yearFrom }} — {{ params.yearTo }}
                  </span>
                </label>
                <div class="flex gap-3 items-center">
                  <select
                    v-model="params.yearFrom"
                    class="flex-1 px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
                  >
                    <option v-for="y in yearOptions" :key="y" :value="y">{{ y }}</option>
                  </select>
                  <span class="text-gray-400 text-sm flex-shrink-0">до</span>
                  <select
                    v-model="params.yearTo"
                    class="flex-1 px-3 py-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
                  >
                    <option v-for="y in yearOptionsTo" :key="y" :value="y">{{ y }}</option>
                  </select>
                </div>

                <!-- Швидкі пресети дат -->
                <div class="flex flex-wrap gap-1.5 mt-2">
                  <button
                    v-for="preset in yearPresets"
                    :key="preset.label"
                    @click="applyYearPreset(preset)"
                    class="px-2.5 py-1 rounded-lg text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-violet-100 dark:hover:bg-violet-900/30 hover:text-violet-700 dark:hover:text-violet-300 transition-all"
                  >
                    {{ preset.label }}
                  </button>
                </div>
              </div>

              <!-- Мінімальний рейтинг -->
              <div>
                <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">
                  Мінімальний рейтинг TMDB
                  <span class="ml-1 text-violet-500 normal-case font-normal">
                    {{ params.minRating > 0 ? `від ${params.minRating}` : 'будь-який' }}
                  </span>
                </label>
                <div class="flex gap-2">
                  <button
                    v-for="r in ratingOptions"
                    :key="r.value"
                    @click="params.minRating = r.value"
                    class="flex-1 py-1.5 rounded-lg text-xs font-semibold border transition-all"
                    :class="params.minRating === r.value
                      ? 'border-violet-500 bg-violet-50 dark:bg-violet-900/20 text-violet-700 dark:text-violet-300'
                      : 'border-gray-200 dark:border-gray-700 text-gray-500 hover:border-gray-300'"
                  >
                    {{ r.label }}
                  </button>
                </div>
              </div>

              <!-- Скинути всі параметри -->
              <button
                v-if="hasCustomParams"
                @click="resetParams"
                class="w-full py-1.5 text-xs text-gray-400 hover:text-red-500 transition-colors"
              >
                ✕ Скинути всі параметри
              </button>

              <!-- Кнопка запуску -->
              <button
                @click="findRandom"
                :disabled="loading"
                class="w-full py-3.5 rounded-2xl font-bold text-base transition-all relative overflow-hidden"
                :class="loading
                  ? 'bg-gray-100 dark:bg-gray-800 text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-violet-500 to-purple-600 hover:from-violet-600 hover:to-purple-700 text-white shadow-lg shadow-violet-200 dark:shadow-violet-900/40 hover:shadow-xl hover:-translate-y-0.5 active:translate-y-0'"
              >
                <Transition name="btn-swap" mode="out-in">
                  <span v-if="loading" key="loading" class="flex items-center justify-center gap-2">
                    <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                    </svg>
                    Шукаю...
                  </span>
                  <span v-else key="idle" class="flex items-center justify-center gap-2">
                    🎲 Знайти випадковий
                  </span>
                </Transition>
              </button>

              <!-- Помилка -->
              <Transition name="error-slide">
                <p v-if="error" class="text-center text-sm text-red-500 -mt-2">
                  {{ error }}
                </p>
              </Transition>

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
  modelValue: { type: Boolean, default: false },
  initialMediaType: { type: String, default: 'movie' },
  genres: { type: Array, default: () => [] }, // передаємо з батьківського компонента
})

const emit = defineEmits(['update:modelValue'])
const router = useRouter()

const currentYear = new Date().getFullYear()

// ─── Стан параметрів ──────────────────────────────────────────
const defaultParams = () => ({
  mediaType: props.initialMediaType,
  genres: [],
  yearFrom: 1990,
  yearTo: currentYear,
  minRating: 0,
})

const params = ref(defaultParams())
const loading = ref(false)
const error   = ref('')

// ─── Computed ──────────────────────────────────────────────────
const yearOptions = computed(() =>
  Array.from({ length: currentYear - 1899 }, (_, i) => currentYear - i)
)
const yearOptionsTo = computed(() =>
  yearOptions.value.filter(y => y >= params.value.yearFrom)
)

const hasCustomParams = computed(() => {
  const d = defaultParams()
  return (
    params.value.genres.length > 0 ||
    params.value.yearFrom !== d.yearFrom ||
    params.value.yearTo   !== d.yearTo   ||
    params.value.minRating !== d.minRating
  )
})

const yearPresets = [
  { label: 'Класика до 1980', from: 1920, to: 1979 },
  { label: '80-ті',           from: 1980, to: 1989 },
  { label: '90-ті',           from: 1990, to: 1999 },
  { label: '2000-ні',         from: 2000, to: 2009 },
  { label: '2010-ні',         from: 2010, to: 2019 },
  { label: 'Свіженьке',       from: 2020, to: currentYear },
]

const ratingOptions = [
  { label: 'Будь-який', value: 0 },
  { label: '6+',  value: 6 },
  { label: '7+',  value: 7 },
  { label: '8+',  value: 8 },
  { label: '9+',  value: 9 },
]

// ─── Методи ────────────────────────────────────────────────────
const toggleGenre = (id) => {
  const idx = params.value.genres.indexOf(id)
  if (idx === -1) params.value.genres.push(id)
  else params.value.genres.splice(idx, 1)
}

const applyYearPreset = (preset) => {
  params.value.yearFrom = preset.from
  params.value.yearTo   = Math.min(preset.to, currentYear)
}

const resetParams = () => {
  const d = defaultParams()
  params.value.genres    = []
  params.value.yearFrom  = d.yearFrom
  params.value.yearTo    = d.yearTo
  params.value.minRating = d.minRating
}

const findRandom = async () => {
  loading.value = true
  error.value   = ''

  try {
    const mediaType = params.value.mediaType

    // Будуємо параметри для discover
    const discoverParams = {
      sort_by: 'popularity.desc',
    }

    if (params.value.genres.length) {
      discoverParams.with_genres = params.value.genres.join(',')
    }

    if (params.value.minRating > 0) {
      // Підкреслення замість крапок — Django views конвертує назад для TMDB
      discoverParams['vote_average_gte'] = params.value.minRating
      discoverParams['vote_count_gte'] = 100 // фільтруємо шлак без оцінок
    }

    // Роки — теж через підкреслення
    if (mediaType === 'movie') {
      if (params.value.yearFrom) discoverParams['primary_release_date_gte'] = `${params.value.yearFrom}-01-01`
      if (params.value.yearTo)   discoverParams['primary_release_date_lte'] = `${params.value.yearTo}-12-31`
    } else {
      if (params.value.yearFrom) discoverParams['first_air_date_gte'] = `${params.value.yearFrom}-01-01`
      if (params.value.yearTo)   discoverParams['first_air_date_lte'] = `${params.value.yearTo}-12-31`
    }

    // Перший запит — дізнаємось скільки всього сторінок
    const firstRes = await moviesAPI.discover({ ...discoverParams, page: 1 }, mediaType)
    const totalPages = Math.min(firstRes.data?.total_pages || 1, 20)

    if (!totalPages || firstRes.data?.total_results === 0) {
      error.value = 'Нічого не знайдено з такими параметрами 😔 Спробуй інший діапазон'
      return
    }

    // Випадкова сторінка
    const randomPage = Math.floor(Math.random() * totalPages) + 1
    let items = firstRes.data?.results || []

    if (randomPage > 1) {
      const pageRes = await moviesAPI.discover({ ...discoverParams, page: randomPage }, mediaType)
      items = pageRes.data?.results || []
    }

    if (!items.length) {
      error.value = 'Спробуй ще раз!'
      return
    }

    // Випадковий елемент
    const randomItem = items[Math.floor(Math.random() * items.length)]

    // Закриваємо модалку і переходимо
    emit('update:modelValue', false)
    router.push({
      name: mediaType === 'movie' ? 'movie-detail' : 'tv-detail',
      params: { id: randomItem.id }
    })

  } catch (e) {
    console.error(e)
    error.value = 'Помилка з\'єднання. Спробуй ще раз'
  } finally {
    loading.value = false
  }
}

// Синхронізуємо mediaType з батьківським
watch(() => props.initialMediaType, (val) => {
  params.value.mediaType = val
})

// Скидаємо помилку при зміні параметрів
watch(params, () => { error.value = '' }, { deep: true })

// Закриття по Escape
const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.modelValue) emit('update:modelValue', false)
}
watch(() => props.modelValue, (val) => {
  if (val) {
    document.addEventListener('keydown', handleKeydown)
    params.value.mediaType = props.initialMediaType
  } else {
    document.removeEventListener('keydown', handleKeydown)
  }
})
</script>

<style scoped>
/* Modal transitions */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.25s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-scale-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.modal-scale-leave-active {
  transition: all 0.2s ease;
}
.modal-scale-enter-from {
  opacity: 0;
  transform: scale(0.9) translateY(10px);
}
.modal-scale-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(5px);
}

/* Button swap */
.btn-swap-enter-active,
.btn-swap-leave-active {
  transition: all 0.2s ease;
}
.btn-swap-enter-from {
  opacity: 0;
  transform: translateY(5px);
}
.btn-swap-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}

/* Error slide */
.error-slide-enter-active,
.error-slide-leave-active {
  transition: all 0.3s ease;
}
.error-slide-enter-from,
.error-slide-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}

/* Scrollbar */
.scrollbar-thin {
  scrollbar-width: thin;
  scrollbar-color: #e5e7eb transparent;
}
.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #e5e7eb;
  border-radius: 2px;
}
</style>