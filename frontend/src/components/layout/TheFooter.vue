<template>
  <footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- About -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            NewsSite
          </h3>
          <p class="text-gray-600 dark:text-gray-400 text-sm">
            Ваше джерело актуальних новин та цікавих статей.
          </p>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Посилання
          </h3>
          <ul class="space-y-2">
            <li v-for="link in quickLinks" :key="link.path">
              <RouterLink
                :to="link.path"
                class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm"
              >
                {{ link.name }}
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- Categories -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Категорії
          </h3>
          <ul class="space-y-2">
            <li v-for="category in categories" :key="category">
              <a
                href="#"
                class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm"
              >
                {{ category }}
              </a>
            </li>
          </ul>
        </div>

        <!-- Contact -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Контакти
          </h3>
          <ul class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <li>Email: info@newssite.com</li>
            <li>Тел: +380 123 456 789</li>
            <li>
              <RouterLink 
                to="/contact"
                class="text-blue-600 dark:text-blue-400 hover:underline"
              >
                Форма зворотного зв'язку
              </RouterLink>
            </li>
          </ul>
        </div>
      </div>

      <!-- Copyright -->
      <div class="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
        <p class="text-center text-gray-600 dark:text-gray-400 text-sm">
          © {{ currentYear }} NewsSite. Всі права захищені.
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

const currentYear = computed(() => new Date().getFullYear())

const quickLinks = [
  { name: 'Головна', path: '/' },
  { name: 'Новини', path: '/posts' },
  { name: 'Про нас', path: '/about' },
  { name: 'Контакти', path: '/contact' },
]

const categories = [
  'Політика',
  'Економіка',
  'Технології',
  'Спорт',
  'Культура',
]
</script>