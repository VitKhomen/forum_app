<template>
  <Teleport to="body">
    <Transition name="person-fade">
      <div
        v-if="modelValue && personId"
        class="fixed inset-0 z-50 overflow-y-auto"
        @keydown.esc="close"
        tabindex="-1"
        ref="modalEl"
      >
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-gray-950/90 backdrop-blur-md" @click="close" />

        <!-- Панель -->
        <div class="relative min-h-full flex items-start justify-center p-4 pt-8 pb-8">
          <Transition name="person-slide" appear>
            <div
              v-if="true"
              class="relative w-full max-w-4xl bg-gray-900 rounded-3xl shadow-2xl overflow-hidden border border-white/5"
            >

              <!-- Закрити -->
              <button
                @click="close"
                class="absolute top-4 right-4 z-20 p-2 rounded-xl bg-black/40 text-white/50 hover:text-white hover:bg-black/60 backdrop-blur-sm transition-all"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>

              <!-- ══ ЗАВАНТАЖЕННЯ ══ -->
              <div v-if="loading" class="flex items-center justify-center h-96">
                <div class="flex flex-col items-center gap-4">
                  <div class="w-16 h-16 rounded-full border-4 border-gray-700 border-t-amber-400 animate-spin" />
                  <p class="text-sm text-gray-500">Завантаження...</p>
                </div>
              </div>

              <!-- ══ КОНТЕНТ ══ -->
              <template v-else-if="person">

                <!-- ХЕДЕР з фото + базова інфо -->
                <div class="relative">
                  <!-- Фоновий blur з фото -->
                  <div
                    v-if="photoUrl"
                    class="absolute inset-0 bg-cover bg-center scale-110 blur-2xl opacity-20"
                    :style="{ backgroundImage: `url(${photoUrl})` }"
                  />
                  <div class="absolute inset-0 bg-gradient-to-b from-gray-900/50 to-gray-900" />

                  <div class="relative z-10 p-6 sm:p-8 flex flex-col sm:flex-row gap-6 items-start">
                    <!-- Фото -->
                    <div class="flex-shrink-0">
                      <div class="w-36 sm:w-44 aspect-[2/3] rounded-2xl overflow-hidden bg-gray-800 shadow-2xl ring-1 ring-white/10">
                        <img
                          v-if="photoUrl"
                          :src="photoUrl"
                          :alt="person.name"
                          class="w-full h-full object-cover"
                        />
                        <div v-else class="w-full h-full flex items-center justify-center text-5xl text-gray-600">
                          👤
                        </div>
                      </div>
                    </div>

                    <!-- Інфо -->
                    <div class="flex-1 min-w-0 pt-2">
                      <!-- Відомість + роль -->
                      <div class="flex items-center gap-2 mb-3 flex-wrap">
                        <span class="text-xs font-semibold px-3 py-1 rounded-full bg-amber-400/10 border border-amber-400/30 text-amber-400">
                          {{ departmentLabel }}
                        </span>
                        <span v-if="person.popularity" class="text-xs text-gray-500 flex items-center gap-1">
                          🔥 {{ Math.round(person.popularity) }} популярність
                        </span>
                      </div>

                      <!-- Ім'я -->
                      <h2 class="text-3xl sm:text-4xl font-black text-white mb-1 leading-tight">
                        {{ person.name }}
                      </h2>
                      <p v-if="person.also_known_as?.length" class="text-gray-500 text-sm mb-4">
                        {{ person.also_known_as[0] }}
                      </p>

                      <!-- Метадані -->
                      <dl class="grid grid-cols-2 gap-x-6 gap-y-2 text-sm mb-5">
                        <div v-if="person.birthday">
                          <dt class="text-gray-500 text-xs">Народився</dt>
                          <dd class="text-white font-medium">{{ formatDate(person.birthday) }}</dd>
                        </div>
                        <div v-if="person.deathday">
                          <dt class="text-gray-500 text-xs">Помер</dt>
                          <dd class="text-gray-300 font-medium">{{ formatDate(person.deathday) }}</dd>
                        </div>
                        <div v-if="age !== null">
                          <dt class="text-gray-500 text-xs">Вік</dt>
                          <dd class="text-white font-medium">{{ age }} років</dd>
                        </div>
                        <div v-if="person.place_of_birth">
                          <dt class="text-gray-500 text-xs">Місце народження</dt>
                          <dd class="text-white font-medium line-clamp-1">{{ person.place_of_birth }}</dd>
                        </div>
                      </dl>

                      <!-- Статистика -->
                      <div class="flex gap-4 text-center">
                        <div class="bg-white/5 rounded-xl px-4 py-2.5 flex-1">
                          <div class="text-xl font-black text-amber-400">{{ movieCreditsCount }}</div>
                          <div class="text-xs text-gray-500 mt-0.5">фільмів</div>
                        </div>
                        <div v-if="tvCreditsCount" class="bg-white/5 rounded-xl px-4 py-2.5 flex-1">
                          <div class="text-xl font-black text-blue-400">{{ tvCreditsCount }}</div>
                          <div class="text-xs text-gray-500 mt-0.5">серіалів</div>
                        </div>
                        <div v-if="person.movie_credits?.crew?.length || person.tv_credits?.crew?.length" class="bg-white/5 rounded-xl px-4 py-2.5 flex-1">
                          <div class="text-xl font-black text-violet-400">{{ crewCreditsCount }}</div>
                          <div class="text-xs text-gray-500 mt-0.5">в команді</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- ══ ТІЛО ══ -->
                <div class="px-6 sm:px-8 pb-8 space-y-8">

                  <!-- Біографія -->
                  <section v-if="person.biography">
                    <h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-3">Біографія</h3>
                    <div
                      class="text-gray-300 text-sm leading-relaxed"
                      :class="{ 'line-clamp-4': !bioExpanded }"
                    >
                      {{ person.biography }}
                    </div>
                    <button
                      v-if="person.biography.length > 400"
                      @click="bioExpanded = !bioExpanded"
                      class="mt-2 text-xs text-amber-400 hover:text-amber-300 transition-colors font-semibold"
                    >
                      {{ bioExpanded ? '↑ Згорнути' : '↓ Читати повністю' }}
                    </button>
                  </section>

                  <!-- Фото галерея -->
                  <section v-if="photos.length > 1">
                    <h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest mb-3">
                      Фотографії <span class="text-gray-600 normal-case font-normal">({{ photos.length }})</span>
                    </h3>
                    <div class="flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
                      <button
                        v-for="(photo, i) in photos.slice(0, 12)"
                        :key="i"
                        @click="activePhoto = i"
                        class="flex-shrink-0 w-16 aspect-[2/3] rounded-lg overflow-hidden ring-2 transition-all"
                        :class="activePhoto === i ? 'ring-amber-400 scale-105' : 'ring-transparent hover:ring-white/30'"
                      >
                        <img
                          :src="`https://image.tmdb.org/t/p/w185${photo.file_path}`"
                          class="w-full h-full object-cover"
                          loading="lazy"
                        />
                      </button>
                    </div>
                  </section>

                  <!-- Таби фільмографії -->
                  <section>
                    <div class="flex items-center justify-between mb-4">
                      <h3 class="text-sm font-bold text-gray-400 uppercase tracking-widest">Фільмографія</h3>
                      <!-- Таб перемикач -->
                      <div class="flex gap-1 bg-gray-800 rounded-xl p-0.5">
                        <button
                          v-if="castMovies.length"
                          @click="creditsTab = 'cast_movie'"
                          class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all"
                          :class="creditsTab === 'cast_movie'
                            ? 'bg-gray-700 text-white shadow'
                            : 'text-gray-500 hover:text-gray-300'"
                        >🎬 Актор</button>
                        <button
                          v-if="castTv.length"
                          @click="creditsTab = 'cast_tv'"
                          class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all"
                          :class="creditsTab === 'cast_tv'
                            ? 'bg-gray-700 text-white shadow'
                            : 'text-gray-500 hover:text-gray-300'"
                        >📺 Серіали</button>
                        <button
                          v-if="crewMovies.length"
                          @click="creditsTab = 'crew'"
                          class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-all"
                          :class="creditsTab === 'crew'
                            ? 'bg-gray-700 text-white shadow'
                            : 'text-gray-500 hover:text-gray-300'"
                        >🎥 Режисер/Продюсер</button>
                      </div>
                    </div>

                    <!-- Список -->
                    <div class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
                      <RouterLink
                        v-for="item in currentCredits.slice(0, showAllCredits ? 999 : 12)"
                        :key="`${item.id}-${item.credit_id}`"
                        :to="creditsTab === 'cast_tv' || creditsTab === 'crew_tv'
                          ? `/tv/${item.id}`
                          : `/movies/${item.id}`"
                        @click="close"
                        class="group"
                      >
                        <div class="aspect-[2/3] rounded-xl overflow-hidden bg-gray-800 mb-1.5 shadow-md group-hover:shadow-xl group-hover:shadow-amber-400/10 transition-all ring-1 ring-white/5 group-hover:ring-amber-400/30">
                          <img
                            v-if="item.poster_path"
                            :src="`https://image.tmdb.org/t/p/w185${item.poster_path}`"
                            :alt="item.title || item.name"
                            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                            loading="lazy"
                          />
                          <div v-else class="w-full h-full flex items-center justify-center text-3xl text-gray-700">🎬</div>
                        </div>
                        <p class="text-xs font-semibold text-gray-300 group-hover:text-amber-400 transition-colors line-clamp-2 leading-snug">
                          {{ item.title || item.name }}
                        </p>
                        <p class="text-xs text-gray-600 mt-0.5">
                          {{ (item.release_date || item.first_air_date)?.slice(0, 4) }}
                          <span v-if="item.character || item.job" class="text-gray-600"> · {{ item.character || item.job }}</span>
                        </p>
                      </RouterLink>
                    </div>

                    <!-- Показати більше -->
                    <button
                      v-if="currentCredits.length > 12"
                      @click="showAllCredits = !showAllCredits"
                      class="mt-4 w-full py-2.5 rounded-xl border border-gray-700 text-sm text-gray-400 hover:text-white hover:border-gray-500 transition-all font-medium"
                    >
                      {{ showAllCredits
                        ? '↑ Показати менше'
                        : `↓ Показати всі ${currentCredits.length} робіт`
                      }}
                    </button>
                  </section>

                </div>

              </template>

              <!-- ══ ПОМИЛКА ══ -->
              <div v-else class="flex flex-col items-center justify-center h-64 text-gray-500">
                <p class="text-4xl mb-3">🎭</p>
                <p>Інформацію не знайдено</p>
              </div>

            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import { moviesAPI } from '@/services/api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  personId:   { type: [Number, String], default: null },
})
const emit = defineEmits(['update:modelValue'])

const modalEl       = ref(null)
const person        = ref(null)
const loading       = ref(false)
const bioExpanded   = ref(false)
const activePhoto   = ref(0)
const creditsTab    = ref('cast_movie')
const showAllCredits = ref(false)

// ─── Computed ──────────────────────────────────────────────────
const photoUrl = computed(() => {
  const path = person.value?.images?.profiles?.[activePhoto.value]?.file_path
    || person.value?.profile_path
  return path ? `https://image.tmdb.org/t/p/w342${path}` : null
})

const photos = computed(() => person.value?.images?.profiles || [])

const departmentLabel = computed(() => {
  const map = {
    Acting:    '🎭 Актор/Акторка',
    Directing: '🎬 Режисер',
    Writing:   '✍️ Сценарист',
    Production:'🎥 Продюсер',
    Camera:    '📷 Оператор',
    Sound:     '🎵 Звукорежисер',
    Crew:      '🔧 Знімальна група',
  }
  return map[person.value?.known_for_department] || person.value?.known_for_department || 'Кіноіндустрія'
})

// Фільмографія — сортуємо по даті (свіжі спочатку)
const sortByDate = (arr, dateField = 'release_date') =>
  [...arr].sort((a, b) =>
    (b[dateField] || '0000').localeCompare(a[dateField] || '0000')
  )

const castMovies = computed(() =>
  sortByDate(person.value?.movie_credits?.cast || [])
)
const castTv = computed(() =>
  sortByDate(person.value?.tv_credits?.cast || [], 'first_air_date')
)
const crewMovies = computed(() => {
  // Дедуплікуємо — один фільм може бути з кількома ролями
  const seen = new Set()
  return sortByDate(
    [...(person.value?.movie_credits?.crew || []), ...(person.value?.tv_credits?.crew || [])]
  ).filter(i => { if (seen.has(i.id)) return false; seen.add(i.id); return true })
})

const currentCredits = computed(() => {
  if (creditsTab.value === 'cast_movie') return castMovies.value
  if (creditsTab.value === 'cast_tv')    return castTv.value
  return crewMovies.value
})

const movieCreditsCount = computed(() => castMovies.value.length)
const tvCreditsCount    = computed(() => castTv.value.length)
const crewCreditsCount  = computed(() => crewMovies.value.length)

const age = computed(() => {
  if (!person.value?.birthday) return null
  const born = new Date(person.value.birthday)
  const end  = person.value.deathday ? new Date(person.value.deathday) : new Date()
  return Math.floor((end - born) / (365.25 * 24 * 60 * 60 * 1000))
})

// ─── Методи ────────────────────────────────────────────────────
const close = () => emit('update:modelValue', false)

const formatDate = (str) => {
  if (!str) return ''
  return new Date(str).toLocaleDateString('uk-UA', { day: 'numeric', month: 'long', year: 'numeric' })
}

const fetchPerson = async () => {
  if (!props.personId) return
  loading.value    = true
  person.value     = null
  bioExpanded.value = false
  activePhoto.value = 0
  showAllCredits.value = false

  try {
    const { data } = await moviesAPI.getPersonById(props.personId)
    person.value = data

    // Вибираємо дефолтний таб
    if (castMovies.value.length) creditsTab.value = 'cast_movie'
    else if (castTv.value.length) creditsTab.value = 'cast_tv'
    else if (crewMovies.value.length) creditsTab.value = 'crew'
  } catch (e) {
    console.error('fetchPerson:', e)
  } finally {
    loading.value = false
    await nextTick()
    modalEl.value?.focus()
  }
}

watch(() => [props.modelValue, props.personId], ([isOpen, id]) => {
  if (isOpen && id) fetchPerson()
})

// Закрити по Escape
const handleGlobalKey = (e) => {
  if (e.key === 'Escape' && props.modelValue) close()
}
watch(() => props.modelValue, (val) => {
  if (val) document.addEventListener('keydown', handleGlobalKey)
  else     document.removeEventListener('keydown', handleGlobalKey)
})
</script>

<style scoped>
.person-fade-enter-active, .person-fade-leave-active { transition: opacity 0.25s ease; }
.person-fade-enter-from,  .person-fade-leave-to      { opacity: 0; }

.person-slide-enter-active { transition: all 0.4s cubic-bezier(0.34, 1.3, 0.64, 1); }
.person-slide-leave-active { transition: all 0.25s ease; }
.person-slide-enter-from   { opacity: 0; transform: scale(0.93) translateY(20px); }
.person-slide-leave-to     { opacity: 0; transform: scale(0.97) translateY(10px); }

.scrollbar-thin { scrollbar-width: thin; scrollbar-color: #374151 transparent; }
.scrollbar-thin::-webkit-scrollbar       { height: 4px; }
.scrollbar-thin::-webkit-scrollbar-track { background: transparent; }
.scrollbar-thin::-webkit-scrollbar-thumb { background: #374151; border-radius: 2px; }
</style>