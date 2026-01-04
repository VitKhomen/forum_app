<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <!-- Profile Header -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">
        Профіль
      </h1>

      <div class="flex items-start gap-6">
        <!-- Avatar -->
        <div class="flex-shrink-0">
          <div class="w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <img
              v-if="authStore.user?.avatar"
              :src="authStore.user.avatar"
              alt="Avatar"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <UserCircleIcon class="w-20 h-20 text-gray-400" />
            </div>
          </div>
        </div>

        <!-- Info -->
        <div class="flex-1">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white">
            {{ authStore.user?.full_name || authStore.user?.username }}
          </h2>
          <p class="text-gray-600 dark:text-gray-400">@{{ authStore.user?.username }}</p>
          <p class="text-gray-600 dark:text-gray-400 mt-2">{{ authStore.user?.email }}</p>
          
          <div class="mt-4 flex gap-6 text-sm">
            <div>
              <span class="font-semibold">{{ authStore.user?.posts_count || 0 }}</span>
              <span class="text-gray-600 dark:text-gray-400"> постів</span>
            </div>
            <div>
              <span class="font-semibold">{{ authStore.user?.comments_count || 0 }}</span>
              <span class="text-gray-600 dark:text-gray-400"> коментарів</span>
            </div>
          </div>

          <p v-if="authStore.user?.bio" class="mt-4 text-gray-700 dark:text-gray-300">
            {{ authStore.user.bio }}
          </p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="mt-6 flex gap-3">
        <RouterLink
          to="/profile/posts"
          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          Мої пости
        </RouterLink>
        <RouterLink
          to="/profile/create-post"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
        >
          Створити пост
        </RouterLink>
        <button
          @click="showEditModal = true"
          class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
        >
          Редагувати профіль
        </button>
      </div>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-600 dark:text-gray-400 text-sm">Пости</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ authStore.user?.posts_count || 0 }}
            </p>
          </div>
          <NewspaperIcon class="w-10 h-10 text-blue-600" />
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-600 dark:text-gray-400 text-sm">Коментарі</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ authStore.user?.comments_count || 0 }}
            </p>
          </div>
          <ChatBubbleLeftIcon class="w-10 h-10 text-green-600" />
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-gray-600 dark:text-gray-400 text-sm">Дата реєстрації</p>
            <p class="text-xl font-bold text-gray-900 dark:text-white">
              {{ formatDate(authStore.user?.created_at) }}
            </p>
          </div>
          <CalendarIcon class="w-10 h-10 text-purple-600" />
        </div>
      </div>
    </div>

    <!-- Edit Modal Placeholder -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-bold mb-4">Редагування профілю</h3>
        <p class="text-gray-600 dark:text-gray-400">Функція редагування профілю буде доступна незабаром...</p>
        <button
          @click="showEditModal = false"
          class="mt-4 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
        >
          Закрити
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { 
  UserCircleIcon, 
  NewspaperIcon, 
  ChatBubbleLeftIcon, 
  CalendarIcon 
} from '@heroicons/vue/24/outline'
import { format } from 'date-fns'
import { uk } from 'date-fns/locale'

const authStore = useAuthStore()
const showEditModal = ref(false)

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    return format(new Date(dateString), 'd MMM yyyy', { locale: uk })
  } catch {
    return dateString
  }
}
</script>