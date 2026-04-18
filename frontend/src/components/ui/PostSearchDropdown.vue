<template>
  <div class="relative" ref="containerRef">
    <!-- Інпут -->
    <div class="relative">
      <MagnifyingGlassIcon
        class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none"
      />
      <input
        ref="inputRef"
        v-model="query"
        type="text"
        :placeholder="placeholder"
        class="w-full pl-9 pr-8 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
               bg-white dark:bg-gray-800 text-gray-900 dark:text-white text-sm
               focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
        @focus="onFocus"
        @keydown.arrow-down.prevent="moveDown"
        @keydown.arrow-up.prevent="moveUp"
        @keydown.enter.prevent="selectActive"
        @keydown.escape="close"
      />
      <!-- Спінер або очистити -->
      <div class="absolute right-2 top-1/2 -translate-y-1/2">
        <div
          v-if="loading"
          class="w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin"
        />
        <button
          v-else-if="query"
          @click="clear"
          class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition"
        >
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Дропдаун -->
    <Transition name="dropdown">
      <div
        v-if="isOpen"
        class="absolute top-full left-0 right-0 mt-1 z-50
               bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700
               rounded-lg shadow-xl overflow-hidden"
      >
        <!-- Результати -->
        <template v-if="results.length">
          <RouterLink
            v-for="(post, index) in results"
            :key="post.id"
            :to="`/posts/${post.slug}`"
            @click="close"
            class="flex items-start gap-3 px-4 py-3 transition-colors cursor-pointer"
            :class="activeIndex === index
              ? 'bg-blue-50 dark:bg-blue-900/30'
              : 'hover:bg-gray-50 dark:hover:bg-gray-700'"
            @mouseenter="activeIndex = index"
          >
            <!-- Прев'ю зображення -->
            <div class="w-12 h-12 rounded-lg overflow-hidden flex-shrink-0 bg-gray-100 dark:bg-gray-700">
              <img
                v-if="post.image"
                :src="post.image"
                :alt="post.title"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center">
                <NewspaperIcon class="w-5 h-5 text-gray-400" />
              </div>
            </div>

            <!-- Текст -->
            <div class="flex-1 min-w-0">
              <!-- Заголовок з підсвіткою -->
              <p
                class="text-sm font-medium text-gray-900 dark:text-white truncate"
                v-html="highlight(post.title, query)"
              />
              <!-- Excerpt -->
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-2">
                {{ stripHtml(post.excerpt || post.content) }}
              </p>
              <!-- Мета -->
              <div class="flex items-center gap-2 mt-1 text-xs text-gray-400 dark:text-gray-500">
                <span v-if="post.category_name" class="text-blue-500">{{ post.category_name }}</span>
                <span v-if="post.category_name">·</span>
                <span>{{ post.author_username }}</span>
                <span>·</span>
                <span>{{ post.views_count }} переглядів</span>
              </div>
            </div>
          </RouterLink>

          <!-- Показати всі результати -->
          <button
            @click="goToSearch"
            class="w-full px-4 py-2.5 text-sm text-blue-600 dark:text-blue-400
                   hover:bg-gray-50 dark:hover:bg-gray-700 transition text-left
                   border-t border-gray-100 dark:border-gray-700 font-medium"
          >
            Показати всі результати для "{{ query }}" →
          </button>
        </template>

        <!-- Порожній стан -->
        <div v-else-if="!loading && query.length >= MIN_QUERY" class="px-4 py-8 text-center">
          <MagnifyingGlassIcon class="w-8 h-8 text-gray-300 dark:text-gray-600 mx-auto mb-2" />
          <p class="text-sm text-gray-500 dark:text-gray-400">Нічого не знайдено</p>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Спробуйте інший запит</p>
        </div>

        <!-- Скелетон під час завантаження -->
        <div v-else-if="loading" class="p-2 space-y-1">
          <div v-for="i in 4" :key="i" class="flex items-center gap-3 px-2 py-2">
            <div class="w-12 h-12 rounded-lg bg-gray-200 dark:bg-gray-700 animate-pulse flex-shrink-0" />
            <div class="flex-1 space-y-1.5">
              <div class="h-4 w-3/4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              <div class="h-3 w-full bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              <div class="h-3 w-1/2 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            </div>
          </div>
        </div>

        <!-- Підказки при порожньому інпуті -->
        <div v-else-if="recentSearches.length" class="py-2">
          <p class="px-4 py-1 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wide">
            Нещодавні пошуки
          </p>
          <button
            v-for="s in recentSearches"
            :key="s"
            @click="applyRecent(s)"
            class="w-full flex items-center gap-2 px-4 py-2 text-sm
                   text-gray-700 dark:text-gray-300
                   hover:bg-gray-50 dark:hover:bg-gray-700 transition text-left"
          >
            <ClockIcon class="w-4 h-4 text-gray-400 flex-shrink-0" />
            <span>{{ s }}</span>
          </button>
          <button
            @click="clearRecent"
            class="w-full px-4 py-1.5 text-xs text-gray-400 hover:text-red-500
                   transition text-left border-t border-gray-100 dark:border-gray-700 mt-1"
          >
            Очистити історію
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  MagnifyingGlassIcon,
  XMarkIcon,
  NewspaperIcon,
  ClockIcon,
} from '@heroicons/vue/24/outline'
import { postsAPI } from '@/services/api'

const props = defineProps({
  placeholder: { type: String, default: 'Пошук постів...' },
  autoFocus:   { type: Boolean, default: false },
})


const router       = useRouter()
const containerRef = ref(null)
const inputRef     = ref(null)
const query        = ref('')
const results      = ref([])
const loading      = ref(false)
const isOpen       = ref(false)
const activeIndex  = ref(-1)

const MIN_QUERY    = 2
const DEBOUNCE_MS  = 350
const MAX_RESULTS  = 6
const RECENT_KEY   = 'post_search_recent'
const MAX_RECENT   = 5

let debounceTimer = null

const emit = defineEmits(['close'])

// ── Нещодавні пошуки ─────────────────────────────────────────

const recentSearches = ref(
  JSON.parse(localStorage.getItem(RECENT_KEY) || '[]')
)

const saveRecent = (q) => {
  const updated = [q, ...recentSearches.value.filter(s => s !== q)].slice(0, MAX_RECENT)
  recentSearches.value = updated
  localStorage.setItem(RECENT_KEY, JSON.stringify(updated))
}

const clearRecent = () => {
  recentSearches.value = []
  localStorage.removeItem(RECENT_KEY)
}

const applyRecent = (s) => {
  query.value = s
  search(s)
}

// ── Пошук ─────────────────────────────────────────────────────

const search = async (q) => {
  if (q.length < MIN_QUERY) {
    results.value = []
    loading.value = false
    return
  }

  loading.value = true
  try {
    const { data } = await postsAPI.getAll({
      search:    q,
      page_size: MAX_RESULTS,
    })
    results.value = data.results || []
    isOpen.value  = true
  } catch {
    results.value = []
  } finally {
    loading.value = false
  }
}

// Debounce — чекаємо поки користувач перестане друкувати
watch(query, (val) => {
  activeIndex.value = -1
  clearTimeout(debounceTimer)

  if (val.length < MIN_QUERY) {
    results.value = []
    loading.value = false
    // Відкриваємо для показу нещодавніх
    if (isOpen.value && recentSearches.value.length) return
    if (!val) isOpen.value = !!recentSearches.value.length
    return
  }

  loading.value = true // показуємо скелетон одразу
  debounceTimer = setTimeout(() => search(val), DEBOUNCE_MS)
})

// ── Підсвітка пошукового слова ───────────────────────────────

const highlight = (text, q) => {
  if (!q || !text) return text
  const escaped = q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  const regex   = new RegExp(`(${escaped})`, 'gi')
  return text.replace(
    regex,
    '<mark class="bg-yellow-200 dark:bg-yellow-800 rounded px-0.5 not-italic">$1</mark>'
  )
}

const stripHtml = (html) => {
  if (!html) return ''
  return html.replace(/<[^>]*>/g, '').slice(0, 100)
}

// ── Навігація клавіатурою ────────────────────────────────────

const moveDown = () => {
  if (activeIndex.value < results.value.length - 1) activeIndex.value++
}

const moveUp = () => {
  if (activeIndex.value > -1) activeIndex.value--
}

const selectActive = () => {
  if (activeIndex.value >= 0 && results.value[activeIndex.value]) {
    router.push(`/posts/${results.value[activeIndex.value].slug}`)
    close()
  } else {
    goToSearch()
  }
}

// ── Відкрити / Закрити ────────────────────────────────────────

const onFocus = () => {
  isOpen.value = true
}

const close = () => {
  isOpen.value    = false
  activeIndex.value = -1
  emit('close')
}

const clear = () => {
  query.value   = ''
  results.value = []
  isOpen.value  = !!recentSearches.value.length
  inputRef.value?.focus()
}

const goToSearch = () => {
  if (!query.value.trim()) return
  saveRecent(query.value.trim())
  router.push({ name: 'posts', query: { search: query.value.trim() } })
  close()
}

// Клік поза компонентом — закриваємо
const handleOutsideClick = (e) => {
  if (!containerRef.value?.contains(e.target)) close()
}

onMounted(() => {
  if (props.autoFocus) {
    nextTick(() => inputRef.value?.focus())
  }
  document.addEventListener('click', handleOutsideClick)
})
onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
  clearTimeout(debounceTimer)
})

</script>

<style scoped>
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>