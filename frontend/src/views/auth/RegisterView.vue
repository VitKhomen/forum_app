<template>
  <div class="max-w-md mx-auto">
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6 text-center">
        Реєстрація
      </h1>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <!-- Avatar -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Аватар (необов'язково)
          </label>
          <div class="flex items-center gap-4">
            <div class="w-20 h-20 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <img
                v-if="avatarPreview"
                :src="avatarPreview"
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

        <!-- Username -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Ім'я користувача *
          </label>
          <input
            v-model="form.username"
            type="text"
            required
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="username"
          />
        </div>

        <!-- Email -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Email *
          </label>
          <input
            v-model="form.email"
            type="email"
            required
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="your@email.com"
          />
        </div>

        <!-- First Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Ім'я
          </label>
          <input
            v-model="form.first_name"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Іван"
          />
        </div>

        <!-- Last Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Прізвище
          </label>
          <input
            v-model="form.last_name"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Іваненко"
          />
        </div>

        <!-- Password -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Пароль *
          </label>
          <input
            v-model="form.password"
            type="password"
            required
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="••••••••"
          />
          <p class="text-xs text-gray-500 mt-1">Мінімум 8 символів</p>
        </div>

        <!-- Password Confirm -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Підтвердження пароля *
          </label>
          <input
            v-model="form.password_confirm"
            type="password"
            required
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="••••••••"
          />
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {{ authStore.loading ? 'Завантаження...' : 'Зареєструватися' }}
        </button>
      </form>

      <!-- Login Link -->
      <div class="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
        Вже є акаунт?
        <RouterLink to="/login" class="text-blue-600 dark:text-blue-400 hover:underline font-medium">
          Увійти
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { UserCircleIcon } from '@heroicons/vue/24/outline'
import { useToast } from 'vue-toastification'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const avatarPreview = ref(null)
const avatarInput = ref(null)

const form = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  password_confirm: '',
  avatar: null
})

const handleAvatarChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Перевірка розміру файлу
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Розмір файлу не повинен перевищувати 5MB')
      event.target.value = ''
      return
    }
    
    // Перевірка типу файлу
    const allowedTypes = ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      toast.error('Дозволені тільки файли JPG, PNG, WEBP')
      event.target.value = ''
      return
    }
    
    form.value.avatar = file
    
    // Створюємо попередній перегляд
    const reader = new FileReader()
    reader.onload = (e) => {
      avatarPreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const handleRegister = async () => {
  // Валідація паролів
  if (form.value.password !== form.value.password_confirm) {
    toast.error('Паролі не співпадають')
    return
  }
  
  // Валідація довжини пароля
  if (form.value.password.length < 8) {
    toast.error('Пароль повинен містити мінімум 8 символів')
    return
  }
  
  // Створюємо FormData для відправки з файлом
  const formData = new FormData()
  formData.append('username', form.value.username)
  formData.append('email', form.value.email)
  formData.append('password', form.value.password)
  formData.append('password_confirm', form.value.password_confirm)
  
  if (form.value.first_name) {
    formData.append('first_name', form.value.first_name)
  }
  if (form.value.last_name) {
    formData.append('last_name', form.value.last_name)
  }
  if (form.value.avatar) {
    formData.append('avatar', form.value.avatar)
  }
  
  const result = await authStore.register(formData)
  if (result.success) {
    router.push('/')
  }
}
</script>