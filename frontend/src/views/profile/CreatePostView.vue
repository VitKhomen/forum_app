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
          rows="12"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Введіть текст поста..."
        ></textarea>
      </div>

      <!-- Main Image -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Головне зображення
        </label>
        
        <div v-if="mainImagePreview" class="mb-3">
          <div class="relative inline-block">
            <img :src="mainImagePreview" alt="Preview" class="h-32 rounded-lg" />
            <button
              type="button"
              @click="removeMainImage"
              class="absolute -top-2 -right-2 bg-red-600 text-white rounded-full p-1 hover:bg-red-700"
            >
              <XMarkIcon class="w-4 h-4" />
            </button>
          </div>
        </div>

        <input
          type="file"
          accept="image/*"
          @change="handleMainImageChange"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p class="text-xs text-gray-500 mt-1">JPG, PNG, WEBP. Макс 10MB</p>
      </div>

      <!-- Additional Images -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Додаткові зображення (макс 10)
        </label>
        
        <div v-if="additionalImagesPreviews.length" class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
          <div v-for="(preview, index) in additionalImagesPreviews" :key="index" class="relative">
            <img :src="preview" alt="Preview" class="w-full h-24 object-cover rounded-lg" />
            <button
              type="button"
              @click="removeAdditionalImage(index)"
              class="absolute -top-2 -right-2 bg-red-600 text-white rounded-full p-1 hover:bg-red-700"
            >
              <XMarkIcon class="w-4 h-4" />
            </button>
          </div>
        </div>

        <input
          v-if="form.additional_images.length < 10"
          type="file"
          accept="image/*"
          multiple
          @change="handleAdditionalImagesChange"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p class="text-xs text-gray-500 mt-1">
          {{ form.additional_images.length }}/10 зображень
        </p>
      </div>

      <!-- Videos -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Відео (макс 5)
        </label>
        
        <div v-if="form.videos.length" class="space-y-2 mb-3">
          <div v-for="(video, index) in form.videos" :key="index" class="flex items-center gap-3 p-3 border border-gray-300 dark:border-gray-600 rounded-lg">
            <div class="w-32 h-20 bg-gray-200 dark:bg-gray-700 rounded flex items-center justify-center">
              <span class="text-xs text-gray-500">Відео</span>
            </div>
            <span class="flex-1 text-sm text-gray-700 dark:text-gray-300">{{ video.name }}</span>
            <button
              type="button"
              @click="removeVideo(index)"
              class="bg-red-600 text-white rounded-full p-1 hover:bg-red-700"
            >
              <XMarkIcon class="w-4 h-4" />
            </button>
          </div>
        </div>

        <input
          v-if="form.videos.length < 5"
          type="file"
          accept="video/*"
          multiple
          @change="handleVideosChange"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p class="text-xs text-gray-500 mt-1">
          MP4, WebM. Макс 100MB на файл. {{ form.videos.length }}/5 відео
        </p>
      </div>

      <!-- Tags -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Теги (через кому "технології, новини, україна")
        </label>
        <input
          v-model="tagsString"
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
import { ref, computed, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { postsAPI, categoriesAPI } from '@/services/api'
import { useToast } from 'vue-toastification'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import api from '@/services/api'

const router = useRouter()
const toast = useToast()

const form = ref({
  title: '',
  content: '',
  category: '',
  main_image: null,
  additional_images: [],
  videos: [],
  tags: [],
  status: 'draft'
})

const categories = ref([])
const loading = ref(false)

const mainImagePreview = ref(null)
const additionalImagesPreviews = ref([])

// Main Image handlers
const handleMainImageChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Розмір файлу не повинен перевищувати 10MB')
      event.target.value = ''
      return
    }
    
    form.value.main_image = file
    
    const reader = new FileReader()
    reader.onload = (e) => {
      mainImagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const removeMainImage = () => {
  form.value.main_image = null
  mainImagePreview.value = null
}

// Additional Images handlers
const handleAdditionalImagesChange = (event) => {
  const files = Array.from(event.target.files)
  const availableSlots = 10 - form.value.additional_images.length
  
  if (files.length > availableSlots) {
    toast.warning(`Можна додати тільки ${availableSlots} зображень`)
    files.splice(availableSlots)
  }
  
  files.forEach(file => {
    if (file.size > 10 * 1024 * 1024) {
      toast.error(`Файл ${file.name} завеликий (макс 10MB)`)
      return
    }
    
    form.value.additional_images.push(file)
    
    const reader = new FileReader()
    reader.onload = (e) => {
      additionalImagesPreviews.value.push(e.target.result)
    }
    reader.readAsDataURL(file)
  })
  
  event.target.value = ''
}

const removeAdditionalImage = (index) => {
  form.value.additional_images.splice(index, 1)
  additionalImagesPreviews.value.splice(index, 1)
}

// Videos handlers
const handleVideosChange = (event) => {
  const files = Array.from(event.target.files)
  const availableSlots = 5 - form.value.videos.length
  
  if (files.length > availableSlots) {
    toast.warning(`Можна додати тільки ${availableSlots} відео`)
    files.splice(availableSlots)
  }
  
  files.forEach(file => {
    if (file.size > 100 * 1024 * 1024) {
      toast.error(`Файл ${file.name} завеликий (макс 100MB)`)
      return
    }
    
    form.value.videos.push(file)
  })
  
  event.target.value = ''
}

const removeVideo = (index) => {
  form.value.videos.splice(index, 1)
}

const handleSubmit = async () => {
  try {
    loading.value = true
    
    // Крок 1: Створюємо пост
    const formData = new FormData()
    formData.append('title', form.value.title)
    formData.append('content', form.value.content)
    formData.append('status', form.value.status)
    
    if (form.value.category) {
      formData.append('category', form.value.category)
    }
    
    if (form.value.main_image) {
      formData.append('image', form.value.main_image)
    }
    
    if (form.value.tags && form.value.tags.length > 0) {
      form.value.tags.forEach(tag => {
        formData.append('tags', tag)
      })
    }

    const { data } = await postsAPI.create(formData)
    
    const postSlug = data.slug

    // Крок 2: Додаємо додаткові зображення
    if (form.value.additional_images.length) {
      try {
        const imagesFormData = new FormData()
        form.value.additional_images.forEach(img => {
          imagesFormData.append('image', img)
        })
        
        await api.post(`/posts/${postSlug}/images/`, imagesFormData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
      } catch (imgError) {
        console.error('Error uploading additional images:', imgError)
        toast.warning('Пост створено, але виникла помилка при завантаженні додаткових зображень')
      }
    }
    
    // Крок 3: Додаємо відео
    if (form.value.videos.length) {
      try {
        const videosFormData = new FormData()
        form.value.videos.forEach(video => {
          videosFormData.append('video', video)
        })
        
        await api.post(`/posts/${postSlug}/videos/`, videosFormData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
      } catch (videoError) {
        console.error('Error uploading videos:', videoError)
        toast.warning('Пост створено, але виникла помилка при завантаженні відео')
      }
    }
    
    toast.success('Пост успішно створено!')
    router.push('/profile/posts')
  } catch (error) {
    console.error('Error creating post:', error)
    const errorMsg = error.response?.data?.detail || 
                     error.response?.data?.message || 
                     'Помилка створення поста'
    toast.error(errorMsg)
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
const tagsString = computed({
  get: () => form.value.tags.join(', '),
  set: (val) => {
    form.value.tags = val
      .split(',')
      .map(t => t.trim())
      .filter(Boolean)
  }
})

onMounted(() => {
  fetchCategories()
})
</script>