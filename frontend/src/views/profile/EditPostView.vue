<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">Редагувати пост</h1>

    <div v-if="initialLoading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Завантаження...</p>
    </div>

    <form v-else @submit.prevent="handleSubmit" class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 space-y-6">
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
        
        <div v-if="currentMainImage" class="mb-3">
          <div class="relative inline-block">
            <img :src="currentMainImage" alt="Current image" class="h-32 rounded-lg" />
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
        
        <!-- Existing Images -->
        <div v-if="existingImages.length" class="mb-3">
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Поточні зображення:</p>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div v-for="img in existingImages" :key="img.id" class="relative">
              <img :src="img.image" :alt="`Image ${img.id}`" class="w-full h-24 object-cover rounded-lg" />
              <button
                type="button"
                @click="removeExistingImage(img.id)"
                class="absolute -top-2 -right-2 bg-red-600 text-white rounded-full p-1 hover:bg-red-700"
              >
                <XMarkIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- New Images Preview -->
        <div v-if="newImagesPreviews.length" class="mb-3">
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Нові зображення:</p>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div v-for="(preview, index) in newImagesPreviews" :key="'new-' + index" class="relative">
              <img :src="preview" alt="New image" class="w-full h-24 object-cover rounded-lg" />
              <button
                type="button"
                @click="removeNewImage(index)"
                class="absolute -top-2 -right-2 bg-red-600 text-white rounded-full p-1 hover:bg-red-700"
              >
                <XMarkIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <input
          v-if="totalImagesCount < 10"
          type="file"
          accept="image/*"
          multiple
          @change="handleAdditionalImagesChange"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p class="text-xs text-gray-500 mt-1">
          {{ totalImagesCount }}/10 зображень
        </p>
      </div>

      <!-- Videos -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Відео (макс 5)
        </label>
        
        <!-- Existing Videos -->
        <div v-if="existingVideos.length" class="mb-3">
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Поточні відео:</p>
          <div class="space-y-2">
            <div v-for="video in existingVideos" :key="video.id" class="flex items-center gap-3 p-3 border border-gray-300 dark:border-gray-600 rounded-lg">
              <video :src="video.video" class="w-32 h-20 object-cover rounded" controls></video>
              <span class="flex-1 text-sm text-gray-700 dark:text-gray-300">{{ getFileName(video.video) }}</span>
              <button
                type="button"
                @click="removeExistingVideo(video.id)"
                class="bg-red-600 text-white rounded-full p-1 hover:bg-red-700"
              >
                <XMarkIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- New Videos -->
        <div v-if="form.new_videos.length" class="mb-3">
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Нові відео:</p>
          <div class="space-y-2">
            <div v-for="(video, index) in form.new_videos" :key="'new-video-' + index" class="flex items-center gap-3 p-3 border border-gray-300 dark:border-gray-600 rounded-lg">
              <div class="w-32 h-20 bg-gray-200 dark:bg-gray-700 rounded flex items-center justify-center">
                <span class="text-xs text-gray-500">Відео</span>
              </div>
              <span class="flex-1 text-sm text-gray-700 dark:text-gray-300">{{ video.name }}</span>
              <button
                type="button"
                @click="removeNewVideo(index)"
                class="bg-red-600 text-white rounded-full p-1 hover:bg-red-700"
              >
                <XMarkIcon class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <input
          v-if="totalVideosCount < 5"
          type="file"
          accept="video/*"
          multiple
          @change="handleVideosChange"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p class="text-xs text-gray-500 mt-1">
          MP4, WebM. Макс 100MB на файл. {{ totalVideosCount }}/5 відео
        </p>
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
          {{ loading ? 'Збереження...' : 'Зберегти зміни' }}
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
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { postsAPI, categoriesAPI } from '@/services/api'
import { useToast } from 'vue-toastification'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import api from '@/services/api'

const router = useRouter()
const route = useRoute()
const toast = useToast()

const form = ref({
  title: '',
  content: '',
  category: '',
  new_main_image: null,
  new_additional_images: [],
  new_videos: [],
  tags: '',
  status: 'draft'
})

const categories = ref([])
const loading = ref(false)
const initialLoading = ref(true)

const currentMainImage = ref(null)
const existingImages = ref([])
const newImagesPreviews = ref([])
const imagesToDelete = ref([])

const existingVideos = ref([])
const videosToDelete = ref([])

const totalImagesCount = computed(() => {
  return existingImages.value.length + form.value.new_additional_images.length
})

const totalVideosCount = computed(() => {
  return existingVideos.value.length + form.value.new_videos.length
})

const getFileName = (url) => {
  return url.split('/').pop()
}

// Main Image handlers
const handleMainImageChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 10 * 1024 * 1024) {
      toast.error('Розмір файлу не повинен перевищувати 10MB')
      event.target.value = ''
      return
    }
    
    form.value.new_main_image = file
    
    const reader = new FileReader()
    reader.onload = (e) => {
      currentMainImage.value = e.target.result
    }
    reader.readAsDataURL(file)
  }
}

const removeMainImage = () => {
  form.value.new_main_image = null
  currentMainImage.value = null
}

// Additional Images handlers
const handleAdditionalImagesChange = (event) => {
  const files = Array.from(event.target.files)
  const availableSlots = 10 - totalImagesCount.value
  
  if (files.length > availableSlots) {
    toast.warning(`Можна додати тільки ${availableSlots} зображень`)
    files.splice(availableSlots)
  }
  
  files.forEach(file => {
    if (file.size > 10 * 1024 * 1024) {
      toast.error(`Файл ${file.name} завеликий (макс 10MB)`)
      return
    }
    
    form.value.new_additional_images.push(file)
    
    const reader = new FileReader()
    reader.onload = (e) => {
      newImagesPreviews.value.push(e.target.result)
    }
    reader.readAsDataURL(file)
  })
  
  event.target.value = ''
}

const removeNewImage = (index) => {
  form.value.new_additional_images.splice(index, 1)
  newImagesPreviews.value.splice(index, 1)
}

const removeExistingImage = (id) => {
  imagesToDelete.value.push(id)
  existingImages.value = existingImages.value.filter(img => img.id !== id)
}

// Videos handlers
const handleVideosChange = (event) => {
  const files = Array.from(event.target.files)
  const availableSlots = 5 - totalVideosCount.value
  
  if (files.length > availableSlots) {
    toast.warning(`Можна додати тільки ${availableSlots} відео`)
    files.splice(availableSlots)
  }
  
  files.forEach(file => {
    if (file.size > 100 * 1024 * 1024) {
      toast.error(`Файл ${file.name} завеликий (макс 100MB)`)
      return
    }
    
    form.value.new_videos.push(file)
  })
  
  event.target.value = ''
}

const removeNewVideo = (index) => {
  form.value.new_videos.splice(index, 1)
}

const removeExistingVideo = (id) => {
  videosToDelete.value.push(id)
  existingVideos.value = existingVideos.value.filter(video => video.id !== id)
}

const handleSubmit = async () => {
  try {
    loading.value = true
    
    // Крок 1: Оновлюємо основні дані поста
    const formData = new FormData()
    formData.append('title', form.value.title)
    formData.append('content', form.value.content)
    formData.append('status', form.value.status)
    
    if (form.value.category) {
      formData.append('category', form.value.category)
    }
    
    if (form.value.new_main_image) {
      formData.append('image', form.value.new_main_image)
    }
    
    if (form.value.tags) {
      formData.append('tags', form.value.tags)
    }

    await postsAPI.update(route.params.slug, formData)
    console.log('✅ Post updated')
    
    // Крок 2: Видаляємо зображення
    if (imagesToDelete.value.length) {
      console.log('Видаляємо зображення з id:', imagesToDelete.value)
      try {
        const res = await postsAPI.bulkDeleteImages(route.params.slug, imagesToDelete.value)
        console.log('Видалення успішно:', res.data)
      } catch (err) {
        console.error('Помилка видалення:')
        console.error('Status:', err.response?.status)
        console.error('Response:', err.response?.data)
      }
    }
    
    // Крок 3: Видаляємо відео
    if (videosToDelete.value.length) {
      try {
        await postsAPI.bulkDeleteVideos(route.params.slug, videosToDelete.value)
        console.log('✅ Videos deleted:', videosToDelete.value)
      } catch (error) {
        console.error('❌ Error deleting videos:', error)
        console.error('Response:', error.response?.data)
        toast.warning('Деякі відео не вдалося видалити')
      }
    }
    
    // Крок 4: Додаємо нові зображення
    if (form.value.new_additional_images.length) {
      try {
        const imagesFormData = new FormData()
        // Пробуємо обидва варіанти: 'image' (singular) і 'images' (plural)
        form.value.new_additional_images.forEach(img => {
          imagesFormData.append('image', img)
        })
        
        await postsAPI.addImages(route.params.slug, imagesFormData)
        console.log('✅ New images uploaded')
      } catch (error) {
        console.error('❌ Error uploading images:', error)
        console.error('Response:', error.response?.data)
        toast.warning('Пост оновлено, але виникла помилка при завантаженні нових зображень')
      }
    }
    
    // Крок 5: Додаємо нові відео
    if (form.value.new_videos.length) {
      try {
        const videosFormData = new FormData()
        form.value.new_videos.forEach(video => {
          videosFormData.append('video', video)
        })
        
        await postsAPI.addVideos(route.params.slug, videosFormData)
        console.log('✅ New videos uploaded')
      } catch (error) {
        console.error('❌ Error uploading videos:', error)
        console.error('Response:', error.response?.data)
        toast.warning('Пост оновлено, але виникла помилка при завантаженні нових відео')
      }
    }
    
    toast.success('Пост успішно оновлено!')
    router.push('/profile/posts')
  } catch (error) {
    console.error('❌ Error updating post:', error)
    const errorMsg = error.response?.data?.detail || 
                     error.response?.data?.message || 
                     'Помилка оновлення поста'
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

const fetchPost = async () => {
  try {
    initialLoading.value = true
    const { data } = await postsAPI.getBySlug(route.params.slug)
    
    form.value = {
      title: data.title,
      content: data.content,
      category: data.category || '',
      new_main_image: null,
      new_additional_images: [],
      new_videos: [],
      tags: Array.isArray(data.tags) ? data.tags.join(', ') : '',
      status: data.status
    }
    
    currentMainImage.value = data.image
    existingImages.value = data.images || []
    existingVideos.value = data.videos || []
    
    console.log('Post loaded:', data)
  } catch (error) {
    console.error('Error fetching post:', error)
    toast.error('Помилка завантаження поста')
    router.push('/profile/posts')
  } finally {
    initialLoading.value = false
  }
}

onMounted(async () => {
  await fetchCategories()
  await fetchPost()
})
</script>