<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">Створити пост</h1>

    <form @submit.prevent="handleSubmit" class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 space-y-6">
      <!-- Title -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Заголовок *
        </label>
        <input
          v-model="form.title"
          type="text"
          required
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Введіть заголовок поста..."
        />
      </div>

      <!-- Category -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Категорія
        </label>
        <select
          v-model="form.category"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Без категорії</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">
            {{ cat.name }}
          </option>
        </select>
      </div>

      <!-- Content -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Контент *
        </label>
        <textarea
          v-model="form.content"
          required
          rows="10"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Введіть текст поста..."
        ></textarea>
      </div>

      <!-- Image -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Головне зображення
        </label>
        <input
          type="file"
          accept="image/*"
          @change="handleImageChange"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <!-- Tags -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Теги (через кому)
        </label>
        <input
          v-model="form.tags"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="технології, новини, україна"
        />
      </div>

      <!-- Status -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Статус
        </label>
        <select
          v-model="form.status"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="draft">Чернетка</option>
          <option value="published">Опублікувати</option>
        </select>
      </div>

      <!-- Submit Buttons -->
      <div class="flex gap-4">
        <button
          type="submit"
          :disabled="loading"
          class="flex-1 bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition"
        >
          {{ loading ? 'Створення...' : 'Створити пост' }}
        </button>
        <RouterLink
          to="/profile/posts"
          class="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition text-center"
        >
          Скасувати
        </RouterLink>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { postsAPI, categoriesAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

const router = useRouter()
const toast = useToast()

const form = ref({
  title: '',
  content: '',
  category: '',
  image: null,
  tags: '',
  status: 'draft'
})

const categories = ref([])
const loading = ref(false)

const handleImageChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    form.value.image = file
  }
}

const handleSubmit = async () => {
  try {
    loading.value = true
    
    const formData = new FormData()
    formData.append('title', form.value.title)
    formData.append('content', form.value.content)
    formData.append('status', form.value.status)
    
    if (form.value.category) {
      formData.append('category', form.value.category)
    }
    
    if (form.value.image) {
      formData.append('image', form.value.image)
    }
    
    if (form.value.tags) {
      formData.append('tags', form.value.tags)
    }

    await postsAPI.create(formData)
    
    toast.success('Пост створено!')
    router.push('/profile/posts')
  } catch (error) {
    console.error('Error creating post:', error)
    toast.error('Помилка створення поста')
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  try {
    const { data } = await categoriesAPI.getAll()
    categories.value = data.results || data
  } catch (error) {
    console.error('Error fetching categories:', error)
  }
}

onMounted(() => {
  fetchCategories()
})
</script>