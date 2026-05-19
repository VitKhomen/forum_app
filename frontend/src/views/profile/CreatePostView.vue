<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">Створити пост</h1>

    <!-- Банер відновлення чернетки -->
    <Transition name="slide-down">
      <div
        v-if="hasSavedDraft"
        class="mb-6 flex items-center justify-between gap-4 px-4 py-3
               bg-amber-50 dark:bg-amber-900/20 border border-amber-200
               dark:border-amber-700 rounded-lg"
      >
        <div class="flex items-center gap-2 text-sm text-amber-800 dark:text-amber-300">
          <span>💾</span>
          <span>
            Є незбережений чернетка від
            <time class="font-medium">{{ formatDraftDate(draftSavedAt) }}</time>
          </span>
        </div>
        <div class="flex gap-2 flex-shrink-0">
          <button
            type="button"
            @click="restoreDraft"
            class="px-3 py-1 text-sm font-medium bg-amber-600 hover:bg-amber-700
                   text-white rounded-lg transition"
          >
            Відновити
          </button>
          <button
            type="button"
            @click="discardDraft"
            class="px-3 py-1 text-sm font-medium bg-white dark:bg-gray-700
                   text-gray-700 dark:text-gray-300 border border-gray-300
                   dark:border-gray-600 rounded-lg hover:bg-gray-50
                   dark:hover:bg-gray-600 transition"
          >
            Відхилити
          </button>
        </div>
      </div>
    </Transition>

    <!-- Індикатор автосейву -->
    <Transition name="fade">
      <div
        v-if="autoSaveStatus"
        class="mb-4 text-xs text-gray-400 dark:text-gray-500 flex items-center gap-1"
      >
        <span v-if="autoSaveStatus === 'saving'">⏳ Зберігаємо чернетку...</span>
        <span v-else-if="autoSaveStatus === 'saved'">✅ Чернетка збережена</span>
      </div>
    </Transition>

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
          Контент (необов'язково)
        </label>
        <RichTextEditor
          v-model="form.content"
          placeholder="Напишіть текст посту..."
        />
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
          Додаткові зображення (макс 20)
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
          v-if="form.additional_images.length < 20"
          type="file"
          accept="image/*"
          multiple
          @change="handleAdditionalImagesChange"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p class="text-xs text-gray-500 mt-1">{{ form.additional_images.length }}/20 зображень</p>
      </div>

      <!-- Videos -->
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Відео (макс 5)
        </label>

        <div v-if="form.videos.length" class="space-y-2 mb-3">
          <div
            v-for="(video, index) in form.videos"
            :key="index"
            class="flex items-center gap-3 p-3 border border-gray-300 dark:border-gray-600 rounded-lg"
          >
            <div class="w-32 h-20 bg-gray-200 dark:bg-gray-700 rounded flex items-center justify-center">
              <span class="text-xs text-gray-500">Відео</span>
            </div>
            <span class="flex-1 text-sm text-gray-700 dark:text-gray-300 truncate">{{ video.name }}</span>
            <button
              type="button"
              @click="removeVideo(index)"
              class="bg-red-600 text-white rounded-full p-1 hover:bg-red-700 flex-shrink-0"
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
          Теги (через кому)
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

      <!-- Кнопка додати опитування -->
      <div v-if="!showPoll">
        <button
          type="button"
          @click="addPoll"
          class="flex items-center gap-2 px-4 py-2 border-2 border-dashed border-gray-300
                dark:border-gray-600 rounded-lg text-gray-500 hover:border-blue-500
                hover:text-blue-600 transition w-full justify-center"
        >
          📊 Додати опитування
        </button>
      </div>

      <PollForm
        v-else
        v-model="pollData"
        @remove="removePoll"
      />

      <!-- Submit -->
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
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { postsAPI, categoriesAPI } from '@/services/api'
import { useToast } from 'vue-toastification'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import api from '@/services/api'
import RichTextEditor from '@/components/ui/RichTextEditor.vue'
import { useDraftAutosave } from '@/composables/useDraftAutosave'
import PollForm from '@/components/posts/PollForm.vue'
import { pollsAPI } from '@/services/api'

const router = useRouter()
const toast  = useToast()

const DRAFT_KEY = 'draft:create-post'

// ── Форма ─────────────────────────────────────────────────────

const form = ref({
  title:             '',
  content:           '',
  category:          '',
  tags:              [],
  status:            'draft',
  // Файли не зберігаємо в localStorage — тільки текстові поля
  additional_images: [],
  videos:            [],
  main_image:        null,
})

const categories              = ref([])
const loading                 = ref(false)
const mainImagePreview        = ref(null)
const additionalImagesPreviews = ref([])

const pollData = ref(null)
const showPoll = ref(false)

const addPoll = () => {
  showPoll.value = true
  pollData.value = { question: '', options: ['', ''], is_multiple: false }
}
const removePoll = () => {
  showPoll.value = false
  pollData.value = null
}

// ── Автосейв ──────────────────────────────────────────────────

const hasSavedDraft  = ref(false)
const draftSavedAt   = ref('')
const autoSaveStatus = ref('') // 'saving' | 'saved' | ''

// Зберігаємо тільки текстові поля (файли не серіалізуються)
const draftFields = computed(() => ({
  title:    form.value.title,
  content:  form.value.content,
  category: form.value.category,
  tags:     form.value.tags,
  status:   form.value.status,
}))

const { loadDraft, saveDraft, clearDraft } = useDraftAutosave(DRAFT_KEY, draftFields)

// Вотчер з індикатором
let saveTimer = null
watch(draftFields, (val) => {
  // Не зберігаємо порожню форму
  if (!val.title && !val.content) return

  autoSaveStatus.value = 'saving'
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    saveDraft(val)
    autoSaveStatus.value = 'saved'
    // Ховаємо індикатор через 2 секунди
    setTimeout(() => { autoSaveStatus.value = '' }, 2000)
  }, 2000)
}, { deep: true })

const restoreDraft = () => {
  const draft = loadDraft()
  if (!draft) return
  const { savedAt, ...data } = draft
  Object.assign(form.value, data)
  hasSavedDraft.value = false
  toast.success('Чернетку відновлено')
}

const discardDraft = () => {
  clearDraft()
  hasSavedDraft.value = false
}

const formatDraftDate = (iso) => {
  if (!iso) return ''
  try {
    return new Intl.DateTimeFormat('uk-UA', {
      day:    'numeric',
      month:  'short',
      hour:   '2-digit',
      minute: '2-digit',
    }).format(new Date(iso))
  } catch {
    return ''
  }
}

// ── Теги ──────────────────────────────────────────────────────

const tagsString = computed({
  get: () => form.value.tags.join(', '),
  set: (val) => {
    form.value.tags = val.split(',').map(t => t.trim()).filter(Boolean)
  },
})

// ── Зображення / Відео ────────────────────────────────────────

const handleMainImageChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) {
    toast.error('Розмір файлу не повинен перевищувати 10MB')
    event.target.value = ''
    return
  }
  form.value.main_image = file
  const reader = new FileReader()
  reader.onload = (e) => { mainImagePreview.value = e.target.result }
  reader.readAsDataURL(file)
}

const removeMainImage = () => {
  form.value.main_image = null
  mainImagePreview.value = null
}

const handleAdditionalImagesChange = (event) => {
  const files = Array.from(event.target.files)
  const slots  = 20 - form.value.additional_images.length
  if (files.length > slots) {
    toast.warning(`Можна додати тільки ${slots} зображень`)
    files.splice(slots)
  }
  files.forEach(file => {
    if (file.size > 10 * 1024 * 1024) {
      toast.error(`Файл ${file.name} завеликий (макс 10MB)`)
      return
    }
    form.value.additional_images.push(file)
    const reader = new FileReader()
    reader.onload = (e) => { additionalImagesPreviews.value.push(e.target.result) }
    reader.readAsDataURL(file)
  })
  event.target.value = ''
}

const removeAdditionalImage = (index) => {
  form.value.additional_images.splice(index, 1)
  additionalImagesPreviews.value.splice(index, 1)
}

const handleVideosChange = (event) => {
  const files = Array.from(event.target.files)
  const slots  = 5 - form.value.videos.length
  if (files.length > slots) {
    toast.warning(`Можна додати тільки ${slots} відео`)
    files.splice(slots)
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

// ── Submit ────────────────────────────────────────────────────

const handleSubmit = async () => {
  try {
    loading.value = true

    const formData = new FormData()
    formData.append('title',   form.value.title)
    formData.append('content', form.value.content)
    formData.append('status',  form.value.status)
    if (form.value.category) formData.append('category', form.value.category)
    if (form.value.main_image) formData.append('image', form.value.main_image)
    form.value.tags.forEach(tag => formData.append('tags', tag))

    const { data } = await postsAPI.create(formData)

    const postId   = data.id
    const postSlug = data.slug

    // Опитування
    if (pollData.value && pollData.value.question && pollData.value.options.filter(Boolean).length >= 2) {
      try {
        await pollsAPI.create({
          post_id:     postId,    
          question:    pollData.value.question,
          options:     pollData.value.options.filter(Boolean),
          is_multiple: pollData.value.is_multiple,
        })
      } catch (e) {
        console.error('Poll помилка:', e.response?.data)
        toast.warning('Пост створено, але помилка при додаванні опитування')
      }
    }

    // Додаткові зображення
    if (form.value.additional_images.length) {
      try {
        const imagesFormData = new FormData()
        form.value.additional_images.forEach(img => imagesFormData.append('image', img))
        await api.post(`/posts/${postSlug}/images/`, imagesFormData)
      } catch {
        toast.warning('Пост створено, але виникла помилка при завантаженні зображень')
      }
    }

    // Відео
    if (form.value.videos.length) {
      try {
        const videosFormData = new FormData()
        form.value.videos.forEach(video => videosFormData.append('video', video))
        await api.post(`/posts/${postSlug}/videos/`, videosFormData)
      } catch {
        toast.warning('Пост створено, але виникла помилка при завантаженні відео')
      }
    }

    clearDraft()
    clearTimeout(saveTimer)

    toast.success('Пост успішно створено!')
    router.push('/profile/posts')
  } catch (error) {
    const msg = error.response?.data?.detail ||
                error.response?.data?.message ||
                'Помилка створення поста'
    toast.error(msg)
  } finally {
    loading.value = false
  }
}

// ── Init ──────────────────────────────────────────────────────

const fetchCategories = async () => {
  try {
    const { data } = await categoriesAPI.getAll()
    categories.value = data.results || data
  } catch {}
}

onMounted(() => {
  fetchCategories()

  // Перевіряємо чи є збережена чернетка
  const draft = loadDraft()
  if (draft?.title || draft?.content) {
    hasSavedDraft.value = true
    draftSavedAt.value  = draft.savedAt || ''
  }
})
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
  max-height: 100px;
}
.slide-down-enter-from,
.slide-down-leave-to {
  max-height: 0;
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>