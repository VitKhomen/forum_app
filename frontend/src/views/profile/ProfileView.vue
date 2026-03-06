<template>
  <div class="max-w-4xl mx-auto space-y-6">

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-gray-200 border-t-blue-500"></div>
    </div>

    <!-- Not Found -->
    <div v-else-if="!profileUser" class="text-center py-20">
      <p class="text-5xl mb-4">👤</p>
      <p class="text-xl text-gray-600 dark:text-gray-400">Користувача не знайдено</p>
      <RouterLink to="/" class="mt-4 inline-block text-blue-600 hover:underline">← На головну</RouterLink>
    </div>

    <template v-else>
      <!-- Profile Header -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">
          {{ isOwnProfile ? 'Профіль' : `@${profileUser.username}` }}
        </h1>

        <div class="flex items-start gap-6">
          <!-- Avatar -->
          <div class="flex-shrink-0">
            <div class="w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <img
                v-if="profileUser.avatar"
                :src="profileUser.avatar"
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
              {{ profileUser.full_name || profileUser.username }}
            </h2>
            <div class="mt-2">
              <AuthorWithKarma
                size="lg"
                :username="profileUser.username"
                :karma="profileUser.karma_points || 0"
                :level="profileUser.karma_level || 1"
                :link="false"
              />
            </div>
            <p v-if="profileUser.bio" class="mt-4 text-gray-700 dark:text-gray-300">
              {{ profileUser.bio }}
            </p>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="mt-6 flex flex-wrap gap-3">
          <!-- Свій профіль -->
          <template v-if="isOwnProfile">
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
              @click="openEditModal"
              class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              Редагувати профіль
            </button>
            <button
              @click="showPasswordModal = true"
              class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
            >
              Змінити пароль
            </button>
          </template>

          <!-- Чужий профіль -->
          <template v-else>
            <RouterLink
              :to="`/posts?author_username=${profileUser.username}`"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Пости користувача
            </RouterLink>
          </template>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 gap-6" :class="isOwnProfile ? 'md:grid-cols-4' : 'md:grid-cols-3'">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-600 dark:text-gray-400 text-sm">Пости</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">
                {{ profileUser.posts_count || 0 }}
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
                {{ profileUser.comments_count || 0 }}
              </p>
            </div>
            <ChatBubbleLeftIcon class="w-10 h-10 text-green-600" />
          </div>
        </div>

        <!-- Лайки — тільки свій профіль -->
        <div v-if="isOwnProfile" class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-600 dark:text-gray-400 text-sm">Лайки</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white">
                {{ profileUser.likes_received_count || 0 }}
              </p>
            </div>
            <HeartIcon class="w-10 h-10 text-red-600" />
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-600 dark:text-gray-400 text-sm">На сайті з</p>
              <p class="text-xl font-bold text-gray-900 dark:text-white">
                {{ formatDate(profileUser.date_joined || profileUser.created_at) }}
              </p>
            </div>
            <CalendarIcon class="w-10 h-10 text-purple-600" />
          </div>
        </div>
      </div>

      <!-- Karma History — тільки свій профіль -->
      <div v-if="isOwnProfile" class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Історія карми</h2>
          <button
            @click="showKarmaModal = true"
            class="flex items-center gap-2 px-4 py-2 text-sm font-medium text-purple-600 dark:text-purple-400 bg-purple-50 dark:bg-purple-900/20 rounded-lg hover:bg-purple-100 dark:hover:bg-purple-900/40 transition-colors"
          >
            <ClockIcon class="w-4 h-4" />
            Переглянути все
          </button>
        </div>
      </div>

      <!-- Кінотека — для всіх -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-5 flex items-center gap-2">
          🎬 {{ isOwnProfile ? 'Моя кінотека' : 'Кінотека' }}
        </h2>
        <ProfileMoviesSection :username="profileUser.username" :readonly="!isOwnProfile" />
      </div>
    </template>

    <!-- Edit Profile Modal (тільки свій профіль) -->
    <template v-if="isOwnProfile">
      <Transition name="modal">
        <div
          v-if="showEditModal"
          class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          @click.self="closeEditModal"
        >
          <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div class="flex justify-between items-center mb-6">
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Редагування профілю</h3>
              <button @click="closeEditModal" class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                <XMarkIcon class="w-6 h-6" />
              </button>
            </div>

            <form @submit.prevent="handleUpdateProfile" class="space-y-4">
              <!-- Avatar -->
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Аватар</label>
                <div class="flex items-center gap-4">
                  <div class="w-20 h-20 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <img
                      v-if="avatarPreview || editForm.avatar"
                      :src="avatarPreview || editForm.avatar"
                      alt="Avatar preview"
                      class="w-full h-full object-cover"
                    />
                    <div v-else class="w-full h-full flex items-center justify-center">
                      <UserCircleIcon class="w-16 h-16 text-gray-400" />
                    </div>
                  </div>
                  <div>
                    <input type="file" accept="image/*" @change="handleAvatarChange" class="hidden" ref="avatarInput" />
                    <button type="button" @click="$refs.avatarInput.click()" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                      Вибрати файл
                    </button>
                    <p class="text-xs text-gray-500 mt-1">JPG, PNG. Макс 5MB</p>
                  </div>
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Ім'я</label>
                <input v-model="editForm.first_name" type="text" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Прізвище</label>
                <input v-model="editForm.last_name" type="text" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Про себе</label>
                <textarea v-model="editForm.bio" rows="4" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="Розкажіть про себе..."></textarea>
              </div>

              <div class="flex gap-3 pt-4">
                <button type="submit" :disabled="authStore.loading" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition">
                  {{ authStore.loading ? 'Збереження...' : 'Зберегти' }}
                </button>
                <button type="button" @click="closeEditModal" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition">
                  Скасувати
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>

      <!-- Change Password Modal -->
      <Transition name="modal">
        <div
          v-if="showPasswordModal"
          class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          @click.self="closePasswordModal"
        >
          <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
            <div class="flex justify-between items-center mb-6">
              <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Зміна пароля</h3>
              <button @click="closePasswordModal" class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                <XMarkIcon class="w-6 h-6" />
              </button>
            </div>

            <form @submit.prevent="handleChangePassword" class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Старий пароль</label>
                <input v-model="passwordForm.old_password" type="password" required class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Новий пароль</label>
                <input v-model="passwordForm.new_password" type="password" required class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Підтвердження пароля</label>
                <input v-model="passwordForm.new_password_confirm" type="password" required class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
              </div>
              <div class="flex gap-3 pt-4">
                <button type="submit" :disabled="authStore.loading" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition">
                  {{ authStore.loading ? 'Збереження...' : 'Змінити пароль' }}
                </button>
                <button type="button" @click="closePasswordModal" class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition">
                  Скасувати
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>

      <KarmaHistoryModal v-model="showKarmaModal" :username="authStore.user?.username || ''" />
    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  UserCircleIcon,
  NewspaperIcon,
  ChatBubbleLeftIcon,
  CalendarIcon,
  XMarkIcon,
  HeartIcon,
  ClockIcon,
} from '@heroicons/vue/24/outline'
import { format } from 'date-fns'
import { uk } from 'date-fns/locale'
import { useToast } from 'vue-toastification'
import AuthorWithKarma from '@/components/ui/KarmaBadge.vue'
import KarmaHistoryModal from '@/components/ui/KarmaHistoryModal.vue'
import ProfileMoviesSection from '@/components/movies/ProfileMoviesSection.vue'
import api from '@/services/api'

const route = useRoute()
const authStore = useAuthStore()
const toast = useToast()

const loading = ref(false)
const publicUser = ref(null) // дані публічного профілю (для чужого)

// Визначаємо чий профіль: якщо є :username в URL і це не наш — чужий
const isOwnProfile = computed(() => {
  const username = route.params.username
  if (!username) return true // /profile — завжди свій
  return authStore.user?.username === username
})

// Дані для відображення: свій → authStore.user, чужий → publicUser
const profileUser = computed(() => {
  if (isOwnProfile.value) return authStore.user
  return publicUser.value
})

// Завантажуємо публічний профіль якщо чужий
const fetchPublicProfile = async (username) => {
  loading.value = true
  try {
    const { data } = await api.get(`/auth/users/${username}/`)
    publicUser.value = data
  } catch {
    publicUser.value = null
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  const username = route.params.username
  if (username && !isOwnProfile.value) {
    fetchPublicProfile(username)
  }
})

// Якщо змінився username в URL (навігація між профілями)
watch(() => route.params.username, (username) => {
  if (username && !isOwnProfile.value) {
    fetchPublicProfile(username)
  }
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    return format(new Date(dateString), 'd MMM yyyy', { locale: uk })
  } catch {
    return dateString
  }
}

// ── Модалки (тільки для свого профілю) ────────────────────────
const showEditModal = ref(false)
const showPasswordModal = ref(false)
const showKarmaModal = ref(false)
const avatarPreview = ref(null)
const avatarInput = ref(null)

const editForm = ref({ first_name: '', last_name: '', bio: '', avatar: null })
const passwordForm = ref({ old_password: '', new_password: '', new_password_confirm: '' })

const openEditModal = () => {
  editForm.value = {
    first_name: authStore.user?.first_name || '',
    last_name:  authStore.user?.last_name  || '',
    bio:        authStore.user?.bio        || '',
    avatar:     authStore.user?.avatar     || null,
  }
  avatarPreview.value = null
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  avatarPreview.value = null
}

const closePasswordModal = () => {
  showPasswordModal.value = false
  passwordForm.value = { old_password: '', new_password: '', new_password_confirm: '' }
}

const handleAvatarChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) { toast.error('Макс 5MB'); return }
  editForm.value.avatar = file
  const reader = new FileReader()
  reader.onload = (e) => { avatarPreview.value = e.target.result }
  reader.readAsDataURL(file)
}

const handleUpdateProfile = async () => {
  const formData = new FormData()
  if (editForm.value.first_name) formData.append('first_name', editForm.value.first_name)
  if (editForm.value.last_name)  formData.append('last_name',  editForm.value.last_name)
  if (editForm.value.bio)        formData.append('bio',        editForm.value.bio)
  if (editForm.value.avatar instanceof File) formData.append('avatar', editForm.value.avatar)

  const result = await authStore.updateProfile(formData)
  if (result.success) {
    closeEditModal()
    await authStore.fetchProfile()
  }
}

const handleChangePassword = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.new_password_confirm) {
    toast.error('Паролі не співпадають'); return
  }
  if (passwordForm.value.new_password.length < 8) {
    toast.error('Мінімум 8 символів'); return
  }
  const result = await authStore.changePassword(passwordForm.value)
  if (result.success) closePasswordModal()
}
</script>

<style scoped>
.modal-enter-active, .modal-leave-active { transition: opacity 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>