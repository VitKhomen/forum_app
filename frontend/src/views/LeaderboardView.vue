<template>
  <div class="max-w-3xl mx-auto px-4 py-8 space-y-6">

    <!-- Header -->
    <div class="text-center mb-8">
      <h1 class="text-4xl font-bold text-gray-900 dark:text-white">🏆 Рейтинг</h1>
      <p class="text-gray-500 dark:text-gray-400 mt-2 text-sm">Найактивніші учасники спільноти</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-gray-200 border-t-purple-500"></div>
    </div>

    <template v-else-if="users.length">

      <!-- TOP 3 Podium -->
      <div v-if="topThree.length === 3" class="grid grid-cols-3 gap-3 items-end mb-8">

        <!-- 2 місце -->
        <div class="flex flex-col items-center">
          <div class="relative mb-3">
            <div class="w-16 h-16 rounded-full overflow-hidden ring-4 ring-gray-300 dark:ring-gray-600 bg-gray-200 dark:bg-gray-700">
              <img v-if="topThree[1].avatar" :src="topThree[1].avatar" class="w-full h-full object-cover" />
              <UserCircleIcon v-else class="w-full h-full text-gray-400 p-1" />
            </div>
            <span class="absolute -bottom-1 -right-1 text-xl">🥈</span>
          </div>
          <p class="font-semibold text-sm text-gray-900 dark:text-white text-center truncate w-full px-1">
            {{ topThree[1].username }}
          </p>
          <AuthorWithKarma
            :username="''"
            :karma="topThree[1].karma_points"
            :level="topThree[1].karma_level"
            size="sm"
          />
          <div class="mt-3 w-full bg-gray-200 dark:bg-gray-700 rounded-t-lg h-16 flex items-center justify-center">
            <span class="text-2xl font-bold text-gray-500 dark:text-gray-400">2</span>
          </div>
        </div>

        <!-- 1 місце (вище) -->
        <div class="flex flex-col items-center">
          <div class="relative mb-3">
            <div class="w-20 h-20 rounded-full overflow-hidden ring-4 ring-yellow-400 bg-gray-200 dark:bg-gray-700 shadow-lg shadow-yellow-400/30">
              <img v-if="topThree[0].avatar" :src="topThree[0].avatar" class="w-full h-full object-cover" />
              <UserCircleIcon v-else class="w-full h-full text-gray-400 p-1" />
            </div>
            <span class="absolute -bottom-1 -right-1 text-2xl">🥇</span>
          </div>
          <p class="font-bold text-base text-gray-900 dark:text-white text-center truncate w-full px-1">
            {{ topThree[0].username }}
          </p>
          <AuthorWithKarma
            :username="''"
            :karma="topThree[0].karma_points"
            :level="topThree[0].karma_level"
            size="sm"
          />
          <div class="mt-3 w-full bg-yellow-400 rounded-t-lg h-28 flex items-center justify-center shadow-lg">
            <span class="text-3xl font-bold text-yellow-900">1</span>
          </div>
        </div>

        <!-- 3 місце -->
        <div class="flex flex-col items-center">
          <div class="relative mb-3">
            <div class="w-16 h-16 rounded-full overflow-hidden ring-4 ring-orange-400 bg-gray-200 dark:bg-gray-700">
              <img v-if="topThree[2].avatar" :src="topThree[2].avatar" class="w-full h-full object-cover" />
              <UserCircleIcon v-else class="w-full h-full text-gray-400 p-1" />
            </div>
            <span class="absolute -bottom-1 -right-1 text-xl">🥉</span>
          </div>
          <p class="font-semibold text-sm text-gray-900 dark:text-white text-center truncate w-full px-1">
            {{ topThree[2].username }}
          </p>
          <AuthorWithKarma
            :username="''"
            :karma="topThree[2].karma_points"
            :level="topThree[2].karma_level"
            size="sm"
          />
          <div class="mt-3 w-full bg-orange-300 dark:bg-orange-700 rounded-t-lg h-10 flex items-center justify-center">
            <span class="text-2xl font-bold text-orange-900 dark:text-orange-200">3</span>
          </div>
        </div>
      </div>

      <!-- Решта користувачів -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
        <div
          v-for="(user, index) in restUsers"
          :key="user.username"
          class="flex items-center gap-4 px-5 py-3.5 border-b border-gray-100 dark:border-gray-700/50 last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/40 transition-colors"
          :class="{ 'bg-purple-50/50 dark:bg-purple-900/10': isCurrentUser(user.username) }"
        >
          <!-- Rank -->
          <span class="w-7 text-center text-sm font-bold text-gray-400 dark:text-gray-500 flex-shrink-0">
            {{ index + 4 }}
          </span>

          <!-- Avatar -->
          <div class="w-9 h-9 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700 flex-shrink-0">
            <img v-if="user.avatar" :src="user.avatar" class="w-full h-full object-cover" />
            <UserCircleIcon v-else class="w-full h-full text-gray-400 p-0.5" />
          </div>

          <!-- Username + badge -->
          <div class="flex-1 min-w-0">
            <AuthorWithKarma
              :username="user.username"
              :karma="user.karma_points"
              :level="user.karma_level"
              size="sm"
            />
          </div>

          <!-- "Це ти" мітка -->
          <span
            v-if="isCurrentUser(user.username)"
            class="text-xs text-purple-600 dark:text-purple-400 font-medium flex-shrink-0"
          >
            це ти
          </span>
        </div>
      </div>

    </template>

    <!-- Empty -->
    <div v-else class="text-center py-20 text-gray-500 dark:text-gray-400">
      <p class="text-5xl mb-4">🏜️</p>
      <p>Поки немає учасників</p>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useKarma } from '@/composables/useKarma'
import { useAuthStore } from '@/stores/auth'
import { UserCircleIcon } from '@heroicons/vue/24/outline'
import AuthorWithKarma from '@/components/ui/KarmaBadge.vue'

const { getLeaderboard } = useKarma()
const authStore = useAuthStore()

const users = ref([])
const loading = ref(false)

const topThree = computed(() => users.value.slice(0, 3))
const restUsers = computed(() => users.value.slice(3))

const isCurrentUser = (username) => authStore.user?.username === username

const loadLeaderboard = async () => {
  loading.value = true
  try {
    users.value = await getLeaderboard(50)
  } finally {
    loading.value = false
  }
}

onMounted(loadLeaderboard)
</script>