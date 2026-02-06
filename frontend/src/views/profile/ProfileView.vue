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
          
          <div class="mt-2">
            <KarmaBadge 
              :karma="authStore.user?.karma_points || 0" 
              :level="authStore.user?.karma_level || 1" 
            />
          </div>
          
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
      <div class="mt-6 flex flex-wrap gap-3">
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

    <div v-if="authStore.user?.username" class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">
        Історія карми
      </h2>
      <KarmaHistory :username="authStore.user.username" :limit="10" />
    </div>

    <!-- Edit Profile Modal -->
    <Transition name="modal">
      <div 
        v-if="showEditModal" 
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
        @click.self="closeEditModal"
      >
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
          <div class="flex justify-between items-center mb-6">
            <h3 class="text-2xl font-bold text-gray-900 dark:text-white">
              Редагування профілю
            </h3>
            <button
              @click="closeEditModal"
              class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            >
              <XMarkIcon class="w-6 h-6" />
            </button>
          </div>

          <form @submit.prevent="handleUpdateProfile" class="space-y-4">
            <!-- Avatar -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Аватар
              </label>
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
                  <input
                    type="file"
                    accept="image/*"
                    @change="handleAvatarChange"
                    class="hidden"
                    ref="avatarInput"
                  />
                  <button
                    type="button"
                    @click="$refs.avatarInput.click()"
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm"
                  >
                    Вибрати файл
                  </button>
                  <p class="text-xs text-gray-500 mt-1">JPG, PNG. Макс 5MB</p>
                </div>
              </div>
            </div>

            <!-- First Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Ім'я
              </label>
              <input
                v-model="editForm.first_name"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- Last Name -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Прізвище
              </label>
              <input
                v-model="editForm.last_name"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- Bio -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Про себе
              </label>
              <textarea
                v-model="editForm.bio"
                rows="4"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Розкажіть про себе..."
              ></textarea>
            </div>

            <!-- Buttons -->
            <div class="flex gap-3 pt-4">
              <button
                type="submit"
                :disabled="authStore.loading"
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
              >
                {{ authStore.loading ? 'Збереження...' : 'Зберегти' }}
              </button>
              <button
                type="button"
                @click="closeEditModal"
                class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
              >
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
            <h3 class="text-2xl font-bold text-gray-900 dark:text-white">
              Зміна пароля
            </h3>
            <button
              @click="closePasswordModal"
              class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            >
              <XMarkIcon class="w-6 h-6" />
            </button>
          </div>

          <form @submit.prevent="handleChangePassword" class="space-y-4">
            <!-- Old Password -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Старий пароль
              </label>
              <input
                v-model="passwordForm.old_password"
                type="password"
                required
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- New Password -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Новий пароль
              </label>
              <input
                v-model="passwordForm.new_password"
                type="password"
                required
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- Confirm Password -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Підтвердження пароля
              </label>
              <input
                v-model="passwordForm.new_password_confirm"
                type="password"
                required
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <!-- Buttons -->
            <div class="flex gap-3 pt-4">
              <button
                type="submit"
                :disabled="authStore.loading"
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
              >
                {{ authStore.loading ? 'Збереження...' : 'Змінити пароль' }}
              </button>
              <button
                type="button"
                @click="closePasswordModal"
                class="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
              >
                Скасувати
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
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
  CalendarIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import { format } from 'date-fns'
import { uk } from 'date-fns/locale'
import { useToast } from 'vue-toastification'
import KarmaBadge from '@/components/ui/KarmaBadge.vue'
import KarmaHistory from '@/components/karma/KarmaHistory.vue'

const authStore = useAuthStore()
const toast = useToast()

const showEditModal = ref(false)
const showPasswordModal = ref(false)
const avatarPreview = ref(null)
const avatarInput = ref(null)

const editForm = ref({
  first_name: '',
  last_name: '',
  bio: '',
  avatar: null
})

const passwordForm = ref({
  old_password: '',
  new_password: '',
  new_password_confirm: ''
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    return format(new Date(dateString), 'd MMM yyyy', { locale: uk })
  } catch {
    return dateString
  }
}

const openEditModal = () => {
  editForm.value = {
    first_name: authStore.user?.first_name || '',
    last_name: authStore.user?.last_name || '',
    bio: authStore.user?.bio || '',
    avatar: authStore.user?.avatar || null
  }
  avatarPreview.value = null
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editForm.value = {
    first_name: '',
    last_name: '',
    bio: '',
    avatar: null
  }
  avatarPreview.value = null
}

const closePasswordModal = () => {
  showPasswordModal.value = false
  passwordForm.value = {
    old_password: '',
    new_password: '',
    new_password_confirm: ''
  }
}

const handleAvatarChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Розмір файлу не повинен перевищувати 5MB')
      return
    }
    
    editForm.value.avatar = file
    
    const reader = new FileReader()
    reader.onload = (e) => {
      avatarPreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const handleUpdateProfile = async () => {
  try {
    const formData = new FormData()
    
    if (editForm.value.first_name) {
      formData.append('first_name', editForm.value.first_name)
    }
    if (editForm.value.last_name) {
      formData.append('last_name', editForm.value.last_name)
    }
    if (editForm.value.bio) {
      formData.append('bio', editForm.value.bio)
    }
    if (editForm.value.avatar instanceof File) {
      formData.append('avatar', editForm.value.avatar)
    }

    const result = await authStore.updateProfile(formData)
    
    if (result.success) {
      closeEditModal()
      // Оновлюємо дані профілю
      await authStore.fetchProfile()
    }
  } catch (error) {
    console.error('Error updating profile:', error)
  }
}

const handleChangePassword = async () => {
  if (passwordForm.value.new_password !== passwordForm.value.new_password_confirm) {
    toast.error('Паролі не співпадають')
    return
  }

  if (passwordForm.value.new_password.length < 8) {
    toast.error('Пароль повинен містити мінімум 8 символів')
    return
  }

  const result = await authStore.changePassword(passwordForm.value)
  
  if (result.success) {
    closePasswordModal()
  }
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .bg-white,
.modal-leave-active .bg-white {
  transition: transform 0.3s ease;
}

.modal-enter-from .bg-white,
.modal-leave-to .bg-white {
  transform: scale(0.9);
}
</style>