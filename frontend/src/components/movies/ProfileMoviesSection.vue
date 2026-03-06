<template>
  <div class="space-y-6">

    <!-- Таби -->
    <div class="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-2xl p-1">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        @click="activeTab = tab.key"
        class="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all"
        :class="activeTab === tab.key
          ? 'bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-white'
          : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300'"
      >
        <span>{{ tab.icon }}</span>
        <span class="hidden sm:inline">{{ tab.label }}</span>
        <span
          v-if="counts[tab.key] > 0"
          class="text-xs px-1.5 py-0.5 rounded-full"
          :class="activeTab === tab.key
            ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400'
            : 'bg-gray-200 dark:bg-gray-600 text-gray-500'"
        >{{ counts[tab.key] }}</span>
      </button>
    </div>

    <!-- Фільтр Фільми/Серіали -->
    <div class="flex items-center justify-between">
      <div class="flex gap-1 bg-gray-100 dark:bg-gray-800 rounded-xl p-0.5">
        <button
          @click="mediaFilter = 'all'"
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
          :class="mediaFilter === 'all' ? 'bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-white' : 'text-gray-400'"
        >Всі</button>
        <button
          @click="mediaFilter = 'movie'"
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
          :class="mediaFilter === 'movie' ? 'bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-white' : 'text-gray-400'"
        >🎬 Фільми</button>
        <button
          @click="mediaFilter = 'tv'"
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
          :class="mediaFilter === 'tv' ? 'bg-white dark:bg-gray-700 shadow-sm text-gray-900 dark:text-white' : 'text-gray-400'"
        >📺 Серіали</button>
      </div>

      <select
        v-if="activeTab === 'ratings'"
        v-model="ratingSort"
        class="px-3 py-1.5 text-xs rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 focus:outline-none"
      >
        <option value="newest">Нові спочатку</option>
        <option value="highest">Висока оцінка</option>
        <option value="lowest">Низька оцінка</option>
      </select>
    </div>

    <!-- Завантаження -->
    <div v-if="loading" class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
      <div v-for="i in 12" :key="i" class="aspect-[2/3] rounded-xl bg-gray-100 dark:bg-gray-800 animate-pulse" />
    </div>

    <template v-else>
      <!-- Порожньо -->
      <div v-if="!filteredItems.length" class="text-center py-16">
        <p class="text-4xl mb-3">{{ currentTab.emptyIcon }}</p>
        <p class="text-gray-500 dark:text-gray-400 font-medium">{{ currentTab.emptyText }}</p>
        <RouterLink
          v-if="!readonly"
          to="/movies"
          class="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-amber-400 hover:bg-amber-300 text-gray-900 rounded-xl text-sm font-semibold transition-colors"
        >
          Перейти до кінотеки →
        </RouterLink>
      </div>

      <!-- Сітка -->
      <div v-else class="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
        <div
          v-for="item in filteredItems"
          :key="`${item.tmdb_id}-${item.media_type}`"
          class="group relative"
        >
          <RouterLink
            :to="item.media_type === 'tv' ? `/tv/${item.tmdb_id}` : `/movies/${item.tmdb_id}`"
            class="block"
          >
            <div class="aspect-[2/3] rounded-xl overflow-hidden bg-gray-100 dark:bg-gray-800 shadow-sm group-hover:shadow-lg transition-all relative">
              <img
                v-if="item.poster_url || item.poster_path"
                :src="item.poster_url || `https://image.tmdb.org/t/p/w342${item.poster_path}`"
                :alt="item.title"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                loading="lazy"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-3xl text-gray-300 dark:text-gray-600">
                {{ item.media_type === 'tv' ? '📺' : '🎬' }}
              </div>

              <!-- Оцінка бейдж -->
              <div
                v-if="activeTab === 'ratings' && item.rating"
                class="absolute top-2 right-2 w-8 h-8 rounded-full flex items-center justify-center text-xs font-black shadow-lg"
                :class="ratingColor(item.rating)"
              >
                {{ item.rating }}
              </div>

              <!-- Кнопка видалення — тільки свій профіль -->
              <div
                v-if="!readonly"
                class="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-all flex items-center justify-center opacity-0 group-hover:opacity-100"
              >
                <button
                  @click.prevent="removeItem(item)"
                  class="w-8 h-8 rounded-full bg-red-500 hover:bg-red-600 text-white flex items-center justify-center shadow-lg transition-colors"
                  title="Видалити"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>

            <p class="text-xs font-medium text-gray-800 dark:text-gray-200 mt-1.5 line-clamp-2 leading-snug group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">
              {{ item.title }}
            </p>
            <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(item.added_at) }}</p>
          </RouterLink>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { moviesAPI } from '@/services/api'
import { useToast } from 'vue-toastification'
import api from '@/services/api'

const props = defineProps({
  username: {
    type: String,
    required: true,
  },
  // true = чужий профіль (без кнопки видалення, публічні ендпоінти)
  readonly: {
    type: Boolean,
    default: false,
  },
})

const toast = useToast()

const activeTab    = ref('watchlist')
const mediaFilter  = ref('all')
const ratingSort   = ref('newest')
const loading      = ref(false)

const watchlist = ref([])
const favorites = ref([])
const ratings   = ref([])

const tabs = [
  { key: 'watchlist', label: 'Хочу дивитись', icon: '🔖', emptyIcon: '🔖', emptyText: 'Список перегляду порожній' },
  { key: 'favorites', label: 'Улюблені',       icon: '❤️', emptyIcon: '❤️', emptyText: 'Улюблених поки немає' },
  { key: 'ratings',   label: 'Оцінки',         icon: '⭐', emptyIcon: '⭐', emptyText: 'Жодного фільму не оцінено' },
]

const currentTab = computed(() => tabs.find(t => t.key === activeTab.value))

const currentList = computed(() => {
  if (activeTab.value === 'watchlist') return watchlist.value
  if (activeTab.value === 'favorites') return favorites.value
  return ratings.value
})

const filteredItems = computed(() => {
  let items = currentList.value
  if (mediaFilter.value !== 'all') {
    items = items.filter(i => i.media_type === mediaFilter.value)
  }
  if (activeTab.value === 'ratings') {
    items = [...items].sort((a, b) => {
      if (ratingSort.value === 'highest') return b.rating - a.rating
      if (ratingSort.value === 'lowest')  return a.rating - b.rating
      return new Date(b.added_at) - new Date(a.added_at)
    })
  }
  return items
})

const counts = computed(() => ({
  watchlist: watchlist.value.length,
  favorites: favorites.value.length,
  ratings:   ratings.value.length,
}))

const fetchAll = async () => {
  loading.value = true
  try {
    if (props.readonly) {
      // Чужий профіль — публічні ендпоінти по username, доступні всім
      const [wl, fav, rat] = await Promise.allSettled([
        api.get(`/movies/users/${props.username}/watchlist/`),
        api.get(`/movies/users/${props.username}/favorites/`),
        api.get(`/movies/users/${props.username}/ratings/`),
      ])
      watchlist.value = wl.value?.data?.results ?? wl.value?.data ?? []
      favorites.value = fav.value?.data?.results ?? fav.value?.data ?? []
      ratings.value   = rat.value?.data?.results ?? rat.value?.data ?? []
    } else {
      // Свій профіль — /me/ ендпоінти (вимагають авторизацію)
      const [wl, fav, rat] = await Promise.allSettled([
        moviesAPI.getMyWatchlist(),
        moviesAPI.getMyFavorites(),
        moviesAPI.getMyRatings(),
      ])
      watchlist.value = wl.value?.data?.results ?? wl.value?.data ?? []
      favorites.value = fav.value?.data?.results ?? fav.value?.data ?? []
      ratings.value   = rat.value?.data?.results ?? rat.value?.data ?? []
    }
  } catch (e) {
    console.error('fetchAll movies:', e)
  } finally {
    loading.value = false
  }
}

const removeItem = async (item) => {
  if (props.readonly) return
  try {
    if (activeTab.value === 'watchlist') {
      await moviesAPI.removeWatchlist(item.tmdb_id, item.media_type)
      watchlist.value = watchlist.value.filter(
        i => !(i.tmdb_id === item.tmdb_id && i.media_type === item.media_type)
      )
      toast.success('Видалено зі списку')
    } else if (activeTab.value === 'favorites') {
      await moviesAPI.removeFavorite(item.tmdb_id, item.media_type)
      favorites.value = favorites.value.filter(
        i => !(i.tmdb_id === item.tmdb_id && i.media_type === item.media_type)
      )
      toast.success('Видалено з улюблених')
    } else if (activeTab.value === 'ratings') {
      await moviesAPI.deleteRating(item.tmdb_id, item.media_type)
      ratings.value = ratings.value.filter(
        i => !(i.tmdb_id === item.tmdb_id && i.media_type === item.media_type)
      )
      toast.success('Оцінку видалено')
    }
  } catch {
    toast.error('Помилка видалення')
  }
}

const ratingColor = (rating) => {
  if (rating >= 8) return 'bg-green-500 text-white'
  if (rating >= 6) return 'bg-amber-400 text-gray-900'
  if (rating >= 4) return 'bg-orange-500 text-white'
  return 'bg-red-500 text-white'
}

const formatDate = (str) => {
  if (!str) return ''
  return new Date(str).toLocaleDateString('uk-UA', { day: 'numeric', month: 'short' })
}

onMounted(fetchAll)
watch(() => props.username, fetchAll)
</script>