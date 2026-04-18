<template>
  <header class="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-50">
    <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">

        <!-- Ліва частина: Burger + Logo -->
        <div class="flex items-center gap-3">
          <button
            @click="sidebarOpen = true"
            class="p-2 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition"
            aria-label="Меню"
          >
            <Bars3Icon class="w-6 h-6" />
          </button>

          <RouterLink to="/" class="flex items-center gap-2">
            <img
              src="https://pub-f6a1145b5cea4dd298fe674249772346.r2.dev/logo/logo.png"
              width="30"
              height="30"
              alt="Logo"
              class="rounded"
            />
            <span class="text-2xl font-bold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition">
              JustForum
            </span>
          </RouterLink>
        </div>

        <!-- Права частина -->
        <div class="flex items-center gap-1">

          <!-- Профіль / Вхід — тільки десктоп -->
          <template v-if="authStore.isAuthenticated">
            <RouterLink
              to="/profile"
              class="hidden md:block text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
            >
              Профіль
            </RouterLink>
            <button
              @click="handleLogout"
              class="hidden md:block text-gray-700 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 px-3 py-2 text-sm font-medium transition"
            >
              Вийти
            </button>
          </template>
          <template v-else>
            <RouterLink
              to="/login"
              class="hidden md:block text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
            >
              Вхід
            </RouterLink>
            <RouterLink
              to="/register"
              class="hidden md:block bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition"
            >
              Реєстрація
            </RouterLink>
          </template>

          <!-- Тема -->
          <ThemeToggle />

          <!-- Фільмотека -->
          <RouterLink
            to="/movies"
            class="relative p-2 rounded-full transition-all group"
            :class="isMoviesRoute
              ? 'text-amber-500 bg-amber-50 dark:bg-amber-900/20'
              : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
            aria-label="Фільмотека"
          >
            <FilmIcon class="w-6 h-6" />
            <span class="absolute -bottom-8 left-1/2 -translate-x-1/2 text-xs bg-gray-900 text-white px-2 py-1 rounded-md whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
              Фільмотека
            </span>
          </RouterLink>

          <!-- Пошук — кнопка + дропдаун -->
          <div class="relative" ref="searchWrapperRef">
            <button
              @click.stop="toggleSearch"
              class="relative p-2 rounded-full transition-all group"
              :class="showSearch
                ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/20'
                : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
              aria-label="Пошук"
            >
              <MagnifyingGlassIcon class="w-6 h-6" />
              <span class="absolute -bottom-8 left-1/2 -translate-x-1/2 text-xs bg-gray-900 text-white px-2 py-1 rounded-md whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                Пошук
              </span>
            </button>

            <!-- Дропдаун -->
            <Transition name="search-drop">
              <div
                v-if="showSearch"
                class="absolute right-0 top-full mt-2 w-80 lg:w-96 z-50"
              >
                <PostSearchDropdown
                  placeholder="Пошук постів..."
                  :auto-focus="true"
                  @close="showSearch = false"
                />
              </div>
            </Transition>
          </div>

        </div>
      </div>
    </nav>
  </header>

  <!-- SIDEBAR -->
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
        @click="sidebarOpen = false"
      />
    </Transition>

    <Transition name="slide-left">
      <div v-if="sidebarOpen" class="fixed top-0 left-0 z-50 h-full w-72 bg-white dark:bg-gray-900 shadow-2xl flex flex-col">

        <!-- Sidebar Header -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-200 dark:border-gray-700">
          <RouterLink to="/" @click="sidebarOpen = false" class="flex items-center gap-2">
            <img
              src="https://pub-f6a1145b5cea4dd298fe674249772346.r2.dev/logo/logo.png"
              width="28" height="28" alt="Logo" class="rounded"
            />
            <span class="text-xl font-bold text-gray-900 dark:text-white">JustForum</span>
          </RouterLink>
          <button
            @click="sidebarOpen = false"
            class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
          >
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <!-- Sidebar Nav -->
        <nav class="flex-1 overflow-y-auto px-3 py-4 space-y-1">

          <p class="px-3 py-1 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
            Навігація
          </p>

          <RouterLink
            v-for="link in mainLinks"
            :key="link.to"
            :to="link.to"
            @click="sidebarOpen = false"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
            :class="isActiveLink(link.to)
              ? 'bg-blue-50 dark:bg-gray-800 text-blue-600 dark:text-blue-400'
              : 'text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-800 hover:text-blue-600 dark:hover:text-blue-400'"
          >
            <component :is="link.icon" class="w-5 h-5 flex-shrink-0" />
            {{ link.label }}
          </RouterLink>

          <!-- Категорії -->
          <div class="pt-2">
            <button
              @click="categoriesExpanded = !categoriesExpanded"
              class="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            >
              <div class="flex items-center gap-3">
                <TagIcon class="w-5 h-5 flex-shrink-0" />
                Категорії
              </div>
              <ChevronDownIcon
                class="w-4 h-4 transition-transform duration-200"
                :class="{ 'rotate-180': categoriesExpanded }"
              />
            </button>

            <Transition name="expand">
              <div
                v-if="categoriesExpanded"
                class="ml-4 mt-1 space-y-0.5 border-l-2 border-gray-200 dark:border-gray-700 pl-3"
              >
                <RouterLink
                  v-for="cat in categories"
                  :key="cat.id"
                  :to="{ name: 'posts', query: { category__slug: cat.slug } }"
                  @click="sidebarOpen = false"
                  class="block px-3 py-2 rounded-lg text-sm text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-gray-800 transition-colors"
                >
                  {{ cat.name }}
                </RouterLink>
              </div>
            </Transition>
          </div>

          <!-- Акаунт -->
          <div class="pt-3">
            <p class="px-3 py-1 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
              Акаунт
            </p>

            <template v-if="authStore.isAuthenticated">
              <RouterLink
                to="/profile"
                @click="sidebarOpen = false"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-800 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              >
                <UserCircleIcon class="w-5 h-5" /> Профіль
              </RouterLink>
              <RouterLink
                to="/profile/create-post"
                @click="sidebarOpen = false"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-gray-800 hover:text-green-600 dark:hover:text-green-400 transition-colors"
              >
                <PencilSquareIcon class="w-5 h-5" /> Створити пост
              </RouterLink>
              <button
                @click="handleLogout"
                class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-gray-800 hover:text-red-600 dark:hover:text-red-400 transition-colors"
              >
                <ArrowRightOnRectangleIcon class="w-5 h-5" /> Вийти
              </button>
            </template>

            <template v-else>
              <RouterLink
                to="/login"
                @click="sidebarOpen = false"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-800 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              >
                <ArrowLeftOnRectangleIcon class="w-5 h-5" /> Вхід
              </RouterLink>
              <RouterLink
                to="/register"
                @click="sidebarOpen = false"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-800 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              >
                <UserPlusIcon class="w-5 h-5" /> Реєстрація
              </RouterLink>
            </template>
          </div>
        </nav>

        <!-- Sidebar Footer — інфо про юзера -->
        <div
          v-if="authStore.isAuthenticated && authStore.user"
          class="px-5 py-4 border-t border-gray-200 dark:border-gray-700"
        >
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700 flex-shrink-0">
              <img
                v-if="authStore.user.avatar"
                :src="authStore.user.avatar"
                class="w-full h-full object-cover"
              />
              <UserCircleIcon v-else class="w-full h-full text-gray-400" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 dark:text-white truncate">
                {{ authStore.user.full_name || authStore.user.username }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                {{ authStore.user.karma_points || 0 }} карми • рівень {{ authStore.user.karma_level || 1 }}
              </p>
            </div>
          </div>
        </div>

      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { categoriesAPI } from '@/services/api'
import {
  Bars3Icon,
  XMarkIcon,
  MagnifyingGlassIcon,
  HomeIcon,
  NewspaperIcon,
  FireIcon,
  ArrowTrendingUpIcon,
  TagIcon,
  UserCircleIcon,
  PencilSquareIcon,
  ArrowRightOnRectangleIcon,
  ArrowLeftOnRectangleIcon,
  UserPlusIcon,
  ChevronDownIcon,
  FilmIcon,
  BookmarkIcon,
} from '@heroicons/vue/24/outline'
import ThemeToggle from '@/components/ui/ThemeToggle.vue'
import PostSearchDropdown from '@/components/ui/PostSearchDropdown.vue'

const router    = useRouter()
const route     = useRoute()
const authStore = useAuthStore()

const sidebarOpen        = ref(false)
const categoriesExpanded = ref(false)
const showSearch         = ref(false)
const categories         = ref([])
const searchWrapperRef   = ref(null)

const isMoviesRoute = computed(() =>
  route.path.startsWith('/movies') || route.path.startsWith('/tv')
)

const mainLinks = [
  { to: '/',                   label: 'Головна',    icon: HomeIcon },
  { to: '/posts',              label: 'Всі пости',  icon: NewspaperIcon },
  { to: '/posts/popular',      label: 'Популярні',  icon: FireIcon },
  { to: '/posts/trending',     label: 'В тренді',   icon: ArrowTrendingUpIcon },
  { to: '/movies',             label: 'Фільмотека', icon: FilmIcon },
  { to: '/profile/bookmarks',  label: 'Закладки',   icon: BookmarkIcon },
]

const isActiveLink = (to) => {
  if (to === '/') return route.path === '/'
  return route.path === to || route.path.startsWith(to + '/')
}

const toggleSearch = () => {
  showSearch.value = !showSearch.value
}

// Закривати при кліку поза блоком пошуку
const handleOutsideClick = (e) => {
  if (!searchWrapperRef.value?.contains(e.target)) {
    showSearch.value = false
  }
}

// Закривати пошук при переході на іншу сторінку
watch(() => route.path, () => {
  sidebarOpen.value = false
  showSearch.value  = false
})

const handleLogout = async () => {
  sidebarOpen.value = false
  await authStore.logout()
  router.push('/')
}

const fetchCategories = async () => {
  try {
    const { data } = await categoriesAPI.getAll()
    categories.value = data.results || data
  } catch {}
}

onMounted(() => {
  fetchCategories()
  document.addEventListener('click', handleOutsideClick)
})

onUnmounted(() => {
  document.removeEventListener('click', handleOutsideClick)
})
</script>

<style scoped>
/* Sidebar overlay */
.fade-enter-active, .fade-leave-active { transition: opacity 0.25s ease }
.fade-enter-from, .fade-leave-to { opacity: 0 }

/* Sidebar drawer */
.slide-left-enter-active, .slide-left-leave-active {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.slide-left-enter-from, .slide-left-leave-to { transform: translateX(-100%) }

/* Категорії розгортання */
.expand-enter-active, .expand-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
  max-height: 500px;
}
.expand-enter-from, .expand-leave-to { max-height: 0; opacity: 0 }

/* Дропдаун пошуку */
.search-drop-enter-active, .search-drop-leave-active {
  transition: all 0.2s ease;
}
.search-drop-enter-from, .search-drop-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
}
</style>