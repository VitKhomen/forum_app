<template>
  <header class="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-50">
    <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">

        <!-- Logo + Burger зліва -->
        <div class="flex items-center gap-3">
          <!-- ✅ Burger кнопка для sidebar -->
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
            <span class="text-2xl font-bold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400">
              JustForum
            </span>
          </RouterLink>
        </div>

        <!-- Desktop: тільки авторизація + тема + пошук -->
        <div class="flex items-center gap-2">
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

          <ThemeToggle />

          <button
            @click="toggleSearch"
            class="p-2 rounded-full text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
            :class="{ 'bg-gray-200 dark:bg-gray-700': showSearch }"
          >
            <MagnifyingGlassIcon class="w-6 h-6" />
          </button>
        </div>
      </div>

      <!-- Панель пошуку -->
      <Transition name="slide-down">
        <div v-if="showSearch" class="border-t border-gray-200 dark:border-gray-700 py-5">
          <div class="flex flex-col sm:flex-row gap-4 items-center">
            <!-- Перемикач типу пошуку -->
            <div class="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-1 gap-1 flex-shrink-0">
              <button
                @click="searchType = 'posts'"
                class="px-3 py-1.5 text-sm font-medium rounded-md transition-all"
                :class="searchType === 'posts'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400'"
              >
                📝 Пости
              </button>
              <button
                @click="searchType = 'movies'"
                class="px-3 py-1.5 text-sm font-medium rounded-md transition-all"
                :class="searchType === 'movies'
                  ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm'
                  : 'text-gray-500 dark:text-gray-400'"
              >
                🎬 Фільми
              </button>
            </div>

            <input
              v-model="searchQuery"
              @keyup.enter="triggerSearch"
              type="search"
              :placeholder="searchType === 'movies' ? 'Назва фільму...' : 'Пошук по заголовку або змісту...'"
              class="flex-1 min-w-[200px] px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
              autofocus
            />

            <!-- Категорія тільки для постів -->
            <select
              v-if="searchType === 'posts'"
              v-model="selectedCategory"
              class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
            >
              <option value="">Всі категорії</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.slug">
                {{ cat.name }}
              </option>
            </select>

            <button
              @click="triggerSearch"
              class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition whitespace-nowrap"
            >
              Шукати
            </button>
          </div>

          <!-- Підказка для фільмів -->
          <p v-if="searchType === 'movies'" class="mt-2 text-xs text-gray-500 dark:text-gray-400">
            🎬 Пошук по базі TMDB — понад 500,000 фільмів
          </p>

          <div v-if="hasActiveFilters && searchType === 'posts'" class="mt-4 flex flex-wrap gap-2">
            <span class="text-sm text-gray-600 dark:text-gray-400">Активні фільтри:</span>
            <span
              v-if="searchQuery"
              class="inline-flex items-center gap-2 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-3 py-1 rounded-full text-sm"
            >
              Пошук: "{{ searchQuery }}"
              <button @click="clearSearch"><XMarkIcon class="w-4 h-4" /></button>
            </span>
            <span
              v-if="selectedCategory"
              class="inline-flex items-center gap-2 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-3 py-1 rounded-full text-sm"
            >
              Категорія: {{ getCategoryName(selectedCategory) }}
              <button @click="clearCategory"><XMarkIcon class="w-4 h-4" /></button>
            </span>
          </div>
        </div>
      </Transition>
    </nav>
  </header>

  <!-- ✅ SIDEBAR DRAWER -->
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition name="fade">
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm"
        @click="sidebarOpen = false"
      />
    </Transition>

    <!-- Drawer -->
    <Transition name="slide-left">
      <div
        v-if="sidebarOpen"
        class="fixed top-0 left-0 z-50 h-full w-72 bg-white dark:bg-gray-900 shadow-2xl flex flex-col"
      >
        <!-- Drawer header -->
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-200 dark:border-gray-700">
          <RouterLink to="/" @click="sidebarOpen = false" class="flex items-center gap-2">
            <img
              src="https://pub-f6a1145b5cea4dd298fe674249772346.r2.dev/logo/logo.png"
              width="28"
              height="28"
              alt="Logo"
              class="rounded"
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

        <!-- Nav links -->
        <nav class="flex-1 overflow-y-auto px-3 py-4 space-y-1">
          <!-- Головні -->
          <p class="px-3 py-1 text-xs font-semibold text-gray-400 dark:text-gray-500 uppercase tracking-wider">
            Навігація
          </p>

          <RouterLink
            v-for="link in mainLinks"
            :key="link.to"
            :to="link.to"
            @click="sidebarOpen = false"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-800 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
            :class="{ 'bg-blue-50 dark:bg-gray-800 text-blue-600 dark:text-blue-400': $route.path === link.to }"
          >
            <component :is="link.icon" class="w-5 h-5 flex-shrink-0" />
            {{ link.label }}
          </RouterLink>

          <!-- Категорії -->
          <div class="pt-3">
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
              <div v-if="categoriesExpanded" class="ml-4 mt-1 space-y-0.5 border-l-2 border-gray-200 dark:border-gray-700 pl-3">
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

          <!-- Авторизація -->
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
                <UserCircleIcon class="w-5 h-5" />
                Профіль
              </RouterLink>
              <RouterLink
                to="/profile/create-post"
                @click="sidebarOpen = false"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-green-50 dark:hover:bg-gray-800 hover:text-green-600 dark:hover:text-green-400 transition-colors"
              >
                <PencilSquareIcon class="w-5 h-5" />
                Створити пост
              </RouterLink>
              <button
                @click="handleLogout"
                class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-red-50 dark:hover:bg-gray-800 hover:text-red-600 dark:hover:text-red-400 transition-colors"
              >
                <ArrowRightOnRectangleIcon class="w-5 h-5" />
                Вийти
              </button>
            </template>

            <template v-else>
              <RouterLink
                to="/login"
                @click="sidebarOpen = false"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-800 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              >
                <ArrowLeftOnRectangleIcon class="w-5 h-5" />
                Вхід
              </RouterLink>
              <RouterLink
                to="/register"
                @click="sidebarOpen = false"
                class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-800 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              >
                <UserPlusIcon class="w-5 h-5" />
                Реєстрація
              </RouterLink>
            </template>
          </div>
        </nav>

        <!-- Drawer footer — karma badge якщо авторизований -->
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
              <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
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
import { ref, computed, watch, onMounted } from 'vue'
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
} from '@heroicons/vue/24/outline'
import ThemeToggle from '@/components/ui/ThemeToggle.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const sidebarOpen = ref(false)
const categoriesExpanded = ref(false)
const showSearch = ref(false)
const searchQuery = ref('')
const selectedCategory = ref('')
const categories = ref([])
const searchType = ref('posts') // 'posts' | 'movies'

// Основні посилання для sidebar
const mainLinks = [
  { to: '/',               label: 'Головна',   icon: HomeIcon },
  { to: '/posts',          label: 'Всі пости', icon: NewspaperIcon },
  { to: '/posts/popular',  label: 'Популярні', icon: FireIcon },
  { to: '/posts/trending', label: 'В тренді',  icon: ArrowTrendingUpIcon },
]

const hasActiveFilters = computed(() => searchQuery.value.trim() || selectedCategory.value)

const getCategoryName = (slug) => {
  const cat = categories.value.find(c => c.slug === slug)
  return cat ? cat.name : slug
}

const toggleSearch = () => {
  showSearch.value = !showSearch.value
  if (showSearch.value) syncFromRoute()
}

const syncFromRoute = () => {
  if (route.query.search) searchQuery.value = route.query.search
  if (route.query.category__slug) selectedCategory.value = route.query.category__slug
}

const triggerSearch = () => {
    if (searchType.value === 'movies') {
      if (!searchQuery.value.trim()) return
      showSearch.value = false
      router.push({ name: 'movie-search', query: { q: searchQuery.value.trim() } })
      return
    }
    
    const query = {}
    if (searchQuery.value.trim()) query.search = searchQuery.value.trim()
    if (selectedCategory.value) query.category__slug = selectedCategory.value
    showSearch.value = false
    router.push({ name: 'posts', query })
  }

const clearSearch = () => { searchQuery.value = ''; triggerSearch() }
const clearCategory = () => { selectedCategory.value = ''; triggerSearch() }

const handleLogout = async () => {
  sidebarOpen.value = false
  await authStore.logout()
  router.push('/')
}

const fetchCategories = async () => {
  try {
    const { data } = await categoriesAPI.getAll()
    categories.value = data.results || data
  } catch (error) {
    console.error('Помилка завантаження категорій:', error)
  }
}

watch(() => route.query, () => {
  if (route.name === 'posts') syncFromRoute()
}, { immediate: true })

// Закривати sidebar при переході
watch(() => route.path, () => {
  sidebarOpen.value = false
})

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
/* Пошук */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  overflow: hidden;
}
.slide-down-enter-from,
.slide-down-leave-to {
  max-height: 0;
  opacity: 0;
}

/* Backdrop */
.fade-enter-active,
.fade-leave-active { transition: opacity 0.25s ease }
.fade-enter-from,
.fade-leave-to { opacity: 0 }

/* Drawer slide from left */
.slide-left-enter-active,
.slide-left-leave-active { transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1) }
.slide-left-enter-from,
.slide-left-leave-to { transform: translateX(-100%) }

/* Категорії expand */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
  max-height: 500px;
}
.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>