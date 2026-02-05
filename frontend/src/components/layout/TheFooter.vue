<template>
  <footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <!-- About -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            JustForum
          </h3>
          <p class="text-gray-600 dark:text-gray-400 text-sm">
            Це сайт форум з мемасиками!
          </p>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Посилання
          </h3>
          <div class="flex flex-wrap gap-x-6 gap-y-2">
            <RouterLink
              v-for="link in quickLinks"
              :key="link.path"
              :to="link.path"
              class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm whitespace-nowrap"
            >
              {{ link.name }}
            </RouterLink>
          </div>
        </div>

        <!-- Contact -->
        <div class="md:ml-auto">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Контакти
          </h3>
          <ul class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <li>
              <a 
                href="https://t.me/Vitaliy_Khomenko" 
                target="_blank" 
                rel="noopener noreferrer"
                class="inline-flex items-center gap-2 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
              >
                <Icon icon="logos:telegram" class="w-6 h-6" />
                Telegram
              </a>
            </li>
            <li>
              <RouterLink 
                to="/contact"
                class="text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm hover:underline"
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
          © {{ currentYear }} JustForum. Всі права не захищені.
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { Icon } from '@iconify/vue'

const currentYear = computed(() => new Date().getFullYear())

const quickLinks = [
  { name: 'Головна', path: '/' },
  { name: 'Всі пости', path: '/posts' },
  { name: 'В тренді', path: '/posts/trending' },
  { name: 'Популярні', path: '/posts/popular' },
  { name: 'Рейтинг', path: '/leaderboard' },
]
</script>