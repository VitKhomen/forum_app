<template>
  <div class="relative w-full" ref="wrapperEl">

    <!-- ═══ Поле пошуку ═══ -->
    <div
      class="flex items-center gap-2 px-4 py-2.5 rounded-2xl border-2 transition-all bg-white dark:bg-gray-900"
      :class="focused
        ? 'border-amber-400 shadow-lg shadow-amber-400/10'
        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'"
    >
      <!-- Іконка пошуку або спінер -->
      <Transition name="icon-swap" mode="out-in">
        <svg v-if="!loading" key="search" class="w-4 h-4 text-gray-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <svg v-else key="spin" class="animate-spin w-4 h-4 text-amber-400 flex-shrink-0" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
      </Transition>

      <input
        ref="inputEl"
        v-model="query"
        @input="onInput"
        @focus="onFocus"
        @keydown.esc="close"
        @keydown.enter="goToSearch"
        type="text"
        :placeholder="placeholder"
        class="flex-1 bg-transparent text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none min-w-0"
      />

      <!-- Очистити -->
      <button v-if="query" @click="clearQuery" class="flex-shrink-0 text-gray-300 hover:text-gray-500 dark:hover:text-gray-200 transition-colors text-lg leading-none">
        ×
      </button>
    </div>

    <!-- ═══ Дропдаун результатів ═══ -->
    <Transition name="results-drop">
      <div
        v-if="showDropdown"
        class="absolute top-full mt-2 left-0 right-0 bg-white dark:bg-gray-900 rounded-2xl shadow-2xl border border-gray-100 dark:border-gray-800 overflow-hidden z-50"
        style="max-height: 520px; overflow-y: auto;"
      >

        <!-- Порожній запит — підказка -->
        <div v-if="!query" class="p-4 text-center text-gray-400 text-sm py-8">
          <p class="text-2xl mb-2">🎬</p>
          Введіть назву фільму, серіалу або ім'я актора
        </div>

        <!-- Є результати -->
        <template v-else-if="hasResults">

          <!-- ПЕРСОНИ -->
          <section v-if="persons.length" class="border-b border-gray-100 dark:border-gray-800">
            <div class="flex items-center justify-between px-4 pt-3 pb-1">
              <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">👤 Актори та режисери</p>
              <span class="text-xs text-gray-300 dark:text-gray-600">{{ persons.length }}</span>
            </div>

            <!-- Горизонтальний скрол для персон -->
            <div class="flex gap-3 px-4 pb-3 overflow-x-auto scrollbar-thin">
              <button
                v-for="person in persons"
                :key="person.id"
                @click="openPerson(person)"
                class="flex flex-col items-center gap-1.5 flex-shrink-0 group"
              >
                <div class="w-14 h-14 rounded-full overflow-hidden bg-gray-100 dark:bg-gray-800 ring-2 ring-transparent group-hover:ring-amber-400 transition-all">
                  <img
                    v-if="person.profile_path"
                    :src="`https://image.tmdb.org/t/p/w185${person.profile_path}`"
                    :alt="person.name"
                    class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    loading="lazy"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center text-xl text-gray-400">👤</div>
                </div>
                <div class="text-center w-16">
                  <p class="text-xs font-semibold text-gray-800 dark:text-gray-200 group-hover:text-amber-500 dark:group-hover:text-amber-400 transition-colors line-clamp-2 leading-tight">
                    {{ person.name }}
                  </p>
                  <p class="text-xs text-gray-400 mt-0.5">{{ deptShort(person.known_for_department) }}</p>
                </div>
              </button>
            </div>
          </section>

          <!-- ФІЛЬМИ -->
          <section v-if="movies.length">
            <div class="flex items-center justify-between px-4 pt-3 pb-1">
              <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">🎬 Фільми</p>
              <span class="text-xs text-gray-300 dark:text-gray-600">{{ movies.length }}</span>
            </div>
            <div>
              <RouterLink
                v-for="item in movies.slice(0, 4)"
                :key="item.id"
                :to="`/movies/${item.id}`"
                @click="close"
                class="flex gap-3 items-center px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group"
              >
                <div class="w-8 aspect-[2/3] flex-shrink-0 rounded-md overflow-hidden bg-gray-100 dark:bg-gray-800">
                  <img v-if="item.poster_path" :src="`https://image.tmdb.org/t/p/w92${item.poster_path}`" class="w-full h-full object-cover" loading="lazy" />
                  <div v-else class="w-full h-full flex items-center justify-center text-xs text-gray-400">🎬</div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors truncate">{{ item.title }}</p>
                  <p class="text-xs text-gray-400">{{ item.release_date?.slice(0,4) }}<span v-if="item.vote_average"> · ⭐ {{ item.vote_average.toFixed(1) }}</span></p>
                </div>
                <svg class="w-3.5 h-3.5 text-gray-300 dark:text-gray-600 group-hover:text-amber-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
              </RouterLink>
            </div>
          </section>

          <!-- СЕРІАЛИ -->
          <section v-if="tvShows.length" :class="movies.length ? 'border-t border-gray-100 dark:border-gray-800' : ''">
            <div class="flex items-center justify-between px-4 pt-3 pb-1">
              <p class="text-xs font-bold text-gray-400 uppercase tracking-widest">📺 Серіали</p>
              <span class="text-xs text-gray-300 dark:text-gray-600">{{ tvShows.length }}</span>
            </div>
            <div>
              <RouterLink
                v-for="item in tvShows.slice(0, 3)"
                :key="item.id"
                :to="`/tv/${item.id}`"
                @click="close"
                class="flex gap-3 items-center px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors group"
              >
                <div class="w-8 aspect-[2/3] flex-shrink-0 rounded-md overflow-hidden bg-gray-100 dark:bg-gray-800">
                  <img v-if="item.poster_path" :src="`https://image.tmdb.org/t/p/w92${item.poster_path}`" class="w-full h-full object-cover" loading="lazy" />
                  <div v-else class="w-full h-full flex items-center justify-center text-xs text-gray-400">📺</div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-semibold text-gray-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors truncate">{{ item.name }}</p>
                  <p class="text-xs text-gray-400">{{ item.first_air_date?.slice(0,4) }}<span v-if="item.vote_average"> · ⭐ {{ item.vote_average.toFixed(1) }}</span></p>
                </div>
                <svg class="w-3.5 h-3.5 text-gray-300 dark:text-gray-600 group-hover:text-amber-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
              </RouterLink>
            </div>
          </section>

          <!-- Показати всі -->
          <div class="px-4 py-3 border-t border-gray-100 dark:border-gray-800">
            <button
              @click="goToSearch"
              class="w-full py-2 rounded-xl bg-gray-50 dark:bg-gray-800 hover:bg-amber-50 dark:hover:bg-amber-900/20 text-sm font-semibold text-gray-600 dark:text-gray-300 hover:text-amber-700 dark:hover:text-amber-400 transition-all border border-gray-100 dark:border-gray-700 hover:border-amber-200 dark:hover:border-amber-800"
            >
              Показати всі результати для "{{ query }}" →
            </button>
          </div>

        </template>

        <!-- Нічого не знайдено -->
        <div v-else-if="!loading && query" class="flex flex-col items-center py-12 text-gray-400">
          <p class="text-3xl mb-3">🔍</p>
          <p class="text-sm font-medium">Нічого не знайдено</p>
          <p class="text-xs mt-1 text-gray-300 dark:text-gray-600">Спробуй іншу назву або ім'я</p>
        </div>

      </div>
    </Transition>

    <!-- PersonModal -->
    <PersonModal
      v-model="showPersonModal"
      :person-id="selectedPersonId"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { moviesAPI } from '@/services/api'
import PersonModal from '@/components/movies/PersonModal.vue'

const props = defineProps({
  placeholder: { type: String, default: 'Пошук фільмів, серіалів, акторів...' },
})

const emit = defineEmits(['search'])

const router = useRouter()
const wrapperEl = ref(null)
const inputEl   = ref(null)

const query   = ref('')
const results = ref([])
const loading = ref(false)
const focused = ref(false)

const showPersonModal  = ref(false)
const selectedPersonId = ref(null)

// ─── Computed ──────────────────────────────────────────────────
const persons = computed(() =>
  results.value.filter(r => r.media_type === 'person').slice(0, 8)
)
const movies = computed(() =>
  results.value.filter(r => r.media_type === 'movie')
    .sort((a, b) => (b.popularity || 0) - (a.popularity || 0))
    .slice(0, 5)
)
const tvShows = computed(() =>
  results.value.filter(r => r.media_type === 'tv')
    .sort((a, b) => (b.popularity || 0) - (a.popularity || 0))
    .slice(0, 4)
)

const hasResults = computed(() =>
  persons.value.length || movies.value.length || tvShows.value.length
)

const showDropdown = computed(() => focused.value && query.value.trim().length >= 1)

// ─── Debounce пошуку ───────────────────────────────────────────
let debounceTimer = null
const onInput = () => {
  clearTimeout(debounceTimer)
  if (!query.value.trim()) { results.value = []; return }
  debounceTimer = setTimeout(fetchResults, 300)
}

// ─── Методи ────────────────────────────────────────────────────
const fetchResults = async () => {
  if (!query.value.trim()) return
  loading.value = true
  try {
    const res = await moviesAPI.search(query.value.trim())
    results.value = res.data?.results || []
  } catch (e) {
    console.error(e)
    results.value = []
  } finally {
    loading.value = false
  }
}

const onFocus = () => { focused.value = true }

const close = () => {
  focused.value = false
}

const clearQuery = () => {
  query.value   = ''
  results.value = []
  inputEl.value?.focus()
}

const goToSearch = () => {
  if (!query.value.trim()) return
  close()
  // Переходимо на сторінку фільмотеки з пошуком
  router.push({ path: '/movies', query: { q: query.value.trim() } })
  emit('search', query.value.trim())
}

const openPerson = (person) => {
  selectedPersonId.value = person.id
  showPersonModal.value  = true
  close()
}

const deptShort = (dept) => {
  const map = { Acting: 'Актор', Directing: 'Режисер', Writing: 'Сценарист', Production: 'Продюсер' }
  return map[dept] || dept || ''
}

// Закрити при кліку поза компонентом
const handleClickOutside = (e) => {
  if (wrapperEl.value && !wrapperEl.value.contains(e.target)) close()
}

onMounted(() => document.addEventListener('mousedown', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('mousedown', handleClickOutside))
</script>

<style scoped>
.results-drop-enter-active { transition: all 0.2s cubic-bezier(0.34, 1.4, 0.64, 1); }
.results-drop-leave-active { transition: all 0.15s ease; }
.results-drop-enter-from   { opacity: 0; transform: translateY(-8px) scale(0.98); }
.results-drop-leave-to     { opacity: 0; transform: translateY(-4px) scale(0.99); }

.icon-swap-enter-active, .icon-swap-leave-active { transition: all 0.15s ease; }
.icon-swap-enter-from    { opacity: 0; transform: scale(0.5) rotate(-90deg); }
.icon-swap-leave-to      { opacity: 0; transform: scale(0.5) rotate(90deg); }

.scrollbar-thin { scrollbar-width: thin; scrollbar-color: #e5e7eb transparent; }
.scrollbar-thin::-webkit-scrollbar       { height: 4px; }
.scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
.scrollbar-thin::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 2px; }
</style>