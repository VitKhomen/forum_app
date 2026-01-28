<template>
  <header class="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-50">
    <nav class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div class="flex items-center gap-3">
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

        <!-- Desktop Navigation + Theme Toggle + Search Icon -->
        <div class="hidden md:flex items-center space-x-6">
          <!-- Основні посилання -->
          <RouterLink
            to="/"
            class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
          >
            Головна
          </RouterLink>
          <RouterLink
            to="/posts"
            class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
          >
            Всі пости
          </RouterLink>
          <RouterLink
            to="/posts/popular"
            class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
          >
            Популярні
          </RouterLink>
          <RouterLink
            to="/posts/trending"
            class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
          >
            В тренді
          </RouterLink>

          <!-- Кнопка Категорії з випадаючим меню -->
          <button
            @click="toggleCategories"
            class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
            :class="{ 'text-blue-600 dark:text-blue-400': showCategories }"
          >
            Категорії
          </button>

          <!-- Авторизація -->
          <template v-if="authStore.isAuthenticated">
            <RouterLink
              to="/profile"
              class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
            >
              Профіль
            </RouterLink>
            <button
              @click="handleLogout"
              class="text-gray-700 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 px-3 py-2 text-sm font-medium transition"
            >
              Вийти
            </button>
          </template>
          <template v-else>
            <RouterLink
              to="/login"
              class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
            >
              Вхід
            </RouterLink>
            <RouterLink
              to="/register"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition"
            >
              Реєстрація
            </RouterLink>
          </template>

          <!-- Перемикач теми -->
          <ThemeToggle />

          <!-- Кнопка пошуку (лупа) -->
          <button
            @click="toggleSearch"
            class="p-2 rounded-full text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
            :class="{ 'bg-gray-200 dark:bg-gray-700': showSearch }"
            aria-label="Пошук"
          >
            <MagnifyingGlassIcon class="w-6 h-6" />
          </button>
        </div>

        <!-- Мобільні кнопки -->
        <div class="md:hidden flex items-center gap-3">
          <!-- Перемикач теми (мобільний) -->
          <ThemeToggle />
          
          <button
            @click="toggleSearch"
            class="p-2 rounded-full text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
            :class="{ 'bg-gray-200 dark:bg-gray-700': showSearch }"
          >
            <MagnifyingGlassIcon class="w-6 h-6" />
          </button>
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="p-2 rounded-full text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
          >
            <Bars3Icon v-if="!mobileMenuOpen" class="w-6 h-6" />
            <XMarkIcon v-else class="w-6 h-6" />
          </button>
        </div>
      </div>

      <!-- Панель категорій (з'являється під хедером) -->
      <Transition name="slide-down">
        <div
          v-if="showCategories"
          class="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 py-5"
        >
          <div class="max-w-7xl mx-auto">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Оберіть категорію</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <RouterLink
                v-for="cat in categories"
                :key="cat.id"
                :to="{ name: 'posts', query: { category__slug: cat.slug } }"
                @click="showCategories = false"
                class="px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white hover:bg-blue-50 dark:hover:bg-blue-900 hover:border-blue-500 transition"
              >
                {{ cat.name }}
              </RouterLink>
            </div>
            <RouterLink
              :to="{ name: 'posts' }"
              @click="showCategories = false"
              class="mt-4 inline-block text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 text-sm font-medium"
            >
              ← Показати всі пости
            </RouterLink>
          </div>
        </div>
      </Transition>

      <!-- Панель пошуку (з'являється під хедером) -->
      <Transition name="slide-down">
        <div
          v-if="showSearch"
          class="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 py-5"
        >
          <div class="max-w-7xl mx-auto">
            <div class="flex flex-col sm:flex-row gap-4 items-center">
              <input
                v-model="searchQuery"
                @keyup.enter="triggerSearch"
                type="search"
                placeholder="Пошук по заголовку або змісту..."
                class="flex-1 min-w-[200px] px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
                autofocus
              />

              <select
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
                class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition shadow-md whitespace-nowrap"
              >
                Шукати
              </button>
            </div>

            <!-- Показуємо активні фільтри -->
            <div v-if="hasActiveFilters" class="mt-4 flex flex-wrap gap-2">
              <span class="text-sm text-gray-600 dark:text-gray-400">Активні фільтри:</span>
              <span
                v-if="searchQuery"
                class="inline-flex items-center gap-2 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-3 py-1 rounded-full text-sm"
              >
                Пошук: "{{ searchQuery }}"
                <button @click="clearSearch" class="hover:text-blue-600">
                  <XMarkIcon class="w-4 h-4" />
                </button>
              </span>
              <span
                v-if="selectedCategory"
                class="inline-flex items-center gap-2 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-3 py-1 rounded-full text-sm"
              >
                Категорія: {{ getCategoryName(selectedCategory) }}
                <button @click="clearCategory" class="hover:text-green-600">
                  <XMarkIcon class="w-4 h-4" />
                </button>
              </span>
            </div>
          </div>
        </div>
      </Transition>

      <!-- Мобільне меню -->
      <Transition name="slide-down">
        <div v-if="mobileMenuOpen && !showSearch && !showCategories" class="md:hidden pb-4 border-t border-gray-200 dark:border-gray-700">
          <div class="flex flex-col space-y-2 pt-4">
            <RouterLink
              to="/"
              @click="mobileMenuOpen = false"
              class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
            >
              Головна
            </RouterLink>
            <RouterLink
              to="/posts"
              @click="mobileMenuOpen = false"
              class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
            >
              Пости
            </RouterLink>
            <button
              @click="toggleCategoriesMobile"
              class="text-left text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
            >
              Категорії
            </button>
            <RouterLink
              to="/contact"
              @click="mobileMenuOpen = false"
              class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
            >
              Контакти
            </RouterLink>

            <template v-if="authStore.isAuthenticated">
              <RouterLink 
                to="/profile" 
                @click="mobileMenuOpen = false" 
                class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
              >
                Профіль
              </RouterLink>
              <button 
                @click="handleLogout" 
                class="text-left text-gray-700 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 px-3 py-2 text-sm font-medium transition"
              >
                Вийти
              </button>
            </template>
            <template v-else>
              <RouterLink 
                to="/login" 
                @click="mobileMenuOpen = false" 
                class="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 px-3 py-2 text-sm font-medium transition"
              >
                Вхід
              </RouterLink>
              <RouterLink 
                to="/register" 
                @click="mobileMenuOpen = false" 
                class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium text-center transition"
              >
                Реєстрація
              </RouterLink>
            </template>
          </div>
        </div>
      </Transition>
    </nav>
  </header>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { RouterLink, useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { categoriesAPI } from '@/services/api'
import {
  Bars3Icon,
  XMarkIcon,
  MagnifyingGlassIcon,
} from '@heroicons/vue/24/outline'
import ThemeToggle from '@/components/ui/ThemeToggle.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const mobileMenuOpen = ref(false)
const showSearch = ref(false)
const showCategories = ref(false)

const searchQuery = ref('')
const selectedCategory = ref('')
const categories = ref([])

const hasActiveFilters = computed(() => {
  return searchQuery.value.trim() || selectedCategory.value
})

const getCategoryName = (slug) => {
  const cat = categories.value.find(c => c.slug === slug)
  return cat ? cat.name : slug
}

const toggleSearch = () => {
  showSearch.value = !showSearch.value
  if (showSearch.value) {
    showCategories.value = false
    mobileMenuOpen.value = false
    syncFromRoute()
  }
}

const toggleCategories = () => {
  showCategories.value = !showCategories.value
  if (showCategories.value) {
    showSearch.value = false
    mobileMenuOpen.value = false
  }
}

const toggleCategoriesMobile = () => {
  mobileMenuOpen.value = false
  showCategories.value = true
}

const syncFromRoute = () => {
  if (route.query.search) {
    searchQuery.value = route.query.search
  }
  if (route.query.category__slug) {
    selectedCategory.value = route.query.category__slug
  }
}

const triggerSearch = () => {
  const query = {}
  
  if (searchQuery.value.trim()) {
    query.search = searchQuery.value.trim()
  }
  
  if (selectedCategory.value) {
    query.category__slug = selectedCategory.value
  }

  showSearch.value = false

  router.push({
    name: 'posts',
    query,
  })
}

const clearSearch = () => {
  searchQuery.value = ''
  triggerSearch()
}

const clearCategory = () => {
  selectedCategory.value = ''
  triggerSearch()
}

const handleLogout = async () => {
  mobileMenuOpen.value = false
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
  if (route.name === 'posts') {
    syncFromRoute()
  }
}, { immediate: true })

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
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
</style>