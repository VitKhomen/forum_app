<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">Редагувати пост</h1>

    <div v-if="initialLoading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600" />
      <p class="mt-4 text-gray-600 dark:text-gray-400">Завантаження...</p>
    </div>

    <template v-else>
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
              Є незбережені зміни від
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
          <span v-if="autoSaveStatus === 'saving'">⏳ Зберігаємо зміни...</span>
          <span v-else-if="autoSaveStatus === 'saved'">✅ Зміни збережено локально</span>
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
            Контент
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

          <div v-if="currentMainImage" class="mb-3">
            <div class="relative inline-block">
              <img :src="currentMainImage" alt="Current image" class="h-32 rounded-lg object-cover" />
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

          <!-- Існуючі -->
          <div v-if="existingImages.length" class="mb-3">
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Поточні зображення:</p>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div v-for="img in existingImages" :key="img.id" class="relative">
                <img :src="img.image" alt="Image" class="w-full h-24 object-cover rounded-lg" />
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

          <!-- Нові -->
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
            v-if="totalImagesCount < 20"
            type="file"
            accept="image/*"
            multiple
            @change="handleAdditionalImagesChange"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <p class="text-xs text-gray-500 mt-1">{{ totalImagesCount }}/20 зображень</p>
        </div>

        <!-- Videos -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Відео (макс 5)
          </label>

          <!-- Існуючі -->
          <div v-if="existingVideos.length" class="mb-3">
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Поточні відео:</p>
            <div class="space-y-2">
              <div
                v-for="video in existingVideos"
                :key="video.id"
                class="flex items-center gap-3 p-3 border border-gray-300 dark:border-gray-600 rounded-lg"
              >
                <video :src="video.video" class="w-32 h-20 object-cover rounded" controls />
                <span class="flex-1 text-sm text-gray-700 dark:text-gray-300 truncate">
                  {{ getFileName(video.video) }}
                </span>
                <button
                  type="button"
                  @click="removeExistingVideo(video.id)"
                  class="bg-red-600 text-white rounded-full p-1 hover:bg-red-700 flex-shrink-0"
                >
                  <XMarkIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <!-- Нові -->
          <div v-if="form.new_videos.length" class="mb-3">
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">Нові відео:</p>
            <div class="space-y-2">
              <div
                v-for="(video, index) in form.new_videos"
                :key="'new-video-' + index"
                class="flex items-center gap-3 p-3 border border-gray-300 dark:border-gray-600 rounded-lg"
              >
                <div class="w-32 h-20 bg-gray-200 dark:bg-gray-700 rounded flex items-center justify-center flex-shrink-0">
                  <span class="text-xs text-gray-500">Відео</span>
                </div>
                <span class="flex-1 text-sm text-gray-700 dark:text-gray-300 truncate">{{ video.name }}</span>
                <button
                  type="button"
                  @click="removeNewVideo(index)"
                  class="bg-red-600 text-white rounded-full p-1 hover:bg-red-700 flex-shrink-0"
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

        <!-- Poll -->
        <div v-if="!showPoll">
          <button
            type="button"
            @click="addPoll"
            class="flex items-center gap-2 px-4 py-2 border-2 border-dashed border-gray-300
                  dark:border-gray-600 rounded-lg text-gray-500 hover:border-blue-500
                  hover:text-blue-600 transition w-full justify-center"
          >
            📊 {{ existingPollId ? 'Опитування видалено — додати нове' : 'Додати опитування' }}
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
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute, RouterLink } from 'vue-router'
import { postsAPI, categoriesAPI } from '@/services/api'
import { useToast } from 'vue-toastification'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import RichTextEditor from '@/components/ui/RichTextEditor.vue'
import { useDraftAutosave } from '@/composables/useDraftAutosave'
import PollForm from '@/components/posts/PollForm.vue'
import { pollsAPI } from '@/services/api'


const router = useRouter()
const route  = useRoute()
const toast  = useToast()

// Ключ унікальний для кожного поста
const DRAFT_KEY = `draft:edit-post:${route.params.slug}`

// ── Форма ─────────────────────────────────────────────────────

const form = ref({
  title:                 '',
  content:               '',
  category:              '',
  tags:                  [],
  status:                'draft',
  new_main_image:        null,
  new_additional_images: [],
  new_videos:            [],
})

const categories             = ref([])
const loading                = ref(false)
const initialLoading         = ref(true)
const currentMainImage       = ref(null)
const existingImages         = ref([])
const newImagesPreviews      = ref([])
const imagesToDelete         = ref([])
const existingVideos         = ref([])
const videosToDelete         = ref([])

// ── Автосейв ──────────────────────────────────────────────────

const hasSavedDraft  = ref(false)
const draftSavedAt   = ref('')
const autoSaveStatus = ref('')

// Зберігаємо тільки текстові поля
const draftFields = computed(() => ({
  title:    form.value.title,
  content:  form.value.content,
  category: form.value.category,
  tags:     form.value.tags,
  status:   form.value.status,
}))

const { loadDraft, saveDraft, clearDraft } = useDraftAutosave(DRAFT_KEY, draftFields)

let saveTimer = null

// Запускаємо вотчер тільки після завантаження поста
const startAutosave = () => {
  watch(draftFields, (val) => {
    autoSaveStatus.value = 'saving'
    clearTimeout(saveTimer)
    saveTimer = setTimeout(() => {
      saveDraft(val)
      autoSaveStatus.value = 'saved'
      setTimeout(() => { autoSaveStatus.value = '' }, 2000)
    }, 2000)
  }, { deep: true })
}

const restoreDraft = () => {
  const draft = loadDraft()
  if (!draft) return
  const { savedAt, ...data } = draft
  Object.assign(form.value, data)
  hasSavedDraft.value = false
  toast.success('Зміни відновлено')
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

onUnmounted(() => clearTimeout(saveTimer))

// ── Poll ──────────────────────────────────────────────────────
const pollData    = ref(null)
const showPoll    = ref(false)
const existingPollId = ref(null)  // id існуючого полла щоб не дублювати

const addPoll = () => {
  showPoll.value = true
  pollData.value = { question: '', options: ['', ''], is_multiple: false }
}

const removePoll = () => {
  showPoll.value = false
  pollData.value = null
}

// ── Computed ──────────────────────────────────────────────────

const totalImagesCount = computed(() =>
  existingImages.value.length + form.value.new_additional_images.length
)

const totalVideosCount = computed(() =>
  existingVideos.value.length + form.value.new_videos.length
)

const tagsString = computed({
  get: () => form.value.tags.join(', '),
  set: (val) => {
    form.value.tags = val.split(',').map(t => t.trim()).filter(Boolean)
  },
})

// ── Зображення ────────────────────────────────────────────────

const handleMainImageChange = (event) => {
  const file = event.target.files[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) {
    toast.error('Розмір файлу не повинен перевищувати 10MB')
    event.target.value = ''
    return
  }
  form.value.new_main_image = file
  const reader = new FileReader()
  reader.onload = (e) => { currentMainImage.value = e.target.result }
  reader.readAsDataURL(file)
}

const removeMainImage = () => {
  form.value.new_main_image = null
  currentMainImage.value    = null
}

const handleAdditionalImagesChange = (event) => {
  const files = Array.from(event.target.files)
  const slots  = 20 - totalImagesCount.value
  if (files.length > slots) {
    toast.warning(`Можна додати тільки ${slots} зображень`)
    files.splice(slots)
  }
  files.forEach(file => {
    if (file.size > 10 * 1024 * 1024) {
      toast.error(`Файл ${file.name} завеликий (макс 10MB)`)
      return
    }
    form.value.new_additional_images.push(file)
    const reader = new FileReader()
    reader.onload = (e) => { newImagesPreviews.value.push(e.target.result) }
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

// ── Відео ─────────────────────────────────────────────────────

const handleVideosChange = (event) => {
  const files = Array.from(event.target.files)
  const slots  = 5 - totalVideosCount.value
  if (files.length > slots) {
    toast.warning(`Можна додати тільки ${slots} відео`)
    files.splice(slots)
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

const removeNewVideo   = (index) => { form.value.new_videos.splice(index, 1) }
const removeExistingVideo = (id) => {
  videosToDelete.value.push(id)
  existingVideos.value = existingVideos.value.filter(v => v.id !== id)
}

const getFileName = (url) => url.split('/').pop()

// ── Submit ────────────────────────────────────────────────────

const handleSubmit = async () => {
  try {
    loading.value = true

    const formData = new FormData()
    formData.append('title',   form.value.title)
    formData.append('content', form.value.content)
    formData.append('status',  form.value.status)
    if (form.value.category)       formData.append('category', form.value.category)
    if (form.value.new_main_image) formData.append('image', form.value.new_main_image)
    form.value.tags.forEach(tag => formData.append('tags', tag))

    await postsAPI.update(route.params.slug, formData)

    // ── Poll ──────────────────────────────────────────────────────
    if (pollData.value && pollData.value.question && pollData.value.options.filter(Boolean).length >= 2) {
      try {
        // pollsAPI.create видаляє старий і створює новий (бо в view є Poll.objects.filter(post=post).delete())
        const { data: updatedPost } = await postsAPI.getBySlug(route.params.slug)
        await pollsAPI.create({
          post_id:     updatedPost.id,
          question:    pollData.value.question,
          options:     pollData.value.options.filter(Boolean),
          is_multiple: pollData.value.is_multiple,
        })
      } catch (e) {
        console.error('Poll помилка:', e.response?.data)
        toast.warning('Пост оновлено, але помилка при збереженні опитування')
      }
    } else if (!showPoll.value && existingPollId.value) {
      // Юзер видалив полл — треба видалити його з бекенду
      try {
        await pollsAPI.delete(existingPollId.value)
      } catch {}
    }

    if (imagesToDelete.value.length) {
      try {
        await postsAPI.bulkDeleteImages(route.params.slug, imagesToDelete.value)
      } catch { toast.warning('Деякі зображення не вдалося видалити') }
    }

    if (videosToDelete.value.length) {
      try {
        await postsAPI.bulkDeleteVideos(route.params.slug, videosToDelete.value)
      } catch { toast.warning('Деякі відео не вдалося видалити') }
    }

    if (form.value.new_additional_images.length) {
      try {
        const imagesFormData = new FormData()
        form.value.new_additional_images.forEach(img => imagesFormData.append('image', img))
        await postsAPI.addImages(route.params.slug, imagesFormData)
      } catch { toast.warning('Пост оновлено, але виникла помилка при завантаженні зображень') }
    }

    if (form.value.new_videos.length) {
      try {
        const videosFormData = new FormData()
        form.value.new_videos.forEach(video => videosFormData.append('video', video))
        await postsAPI.addVideos(route.params.slug, videosFormData)
      } catch { toast.warning('Пост оновлено, але виникла помилка при завантаженні відео') }
    }

    // Чистимо чернетку після успішного збереження
    clearDraft()
    clearTimeout(saveTimer)

    toast.success('Пост успішно оновлено!')
    router.push('/profile/posts')
  } catch (error) {
    const msg = error.response?.data?.detail ||
                error.response?.data?.message ||
                'Помилка оновлення поста'
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

const fetchPost = async () => {
  try {
    initialLoading.value = true
    const { data } = await postsAPI.getBySlug(route.params.slug)

    form.value = {
      title:                 data.title,
      content:               data.content || '',
      category:              data.category || '',
      tags:                  Array.isArray(data.tags) ? [...data.tags] : [],
      status:                data.status,
      new_main_image:        null,
      new_additional_images: [],
      new_videos:            [],
    }

    currentMainImage.value = data.image    || null
    existingImages.value   = data.images   || []
    existingVideos.value   = data.videos   || []

    // Якщо пост вже має полл — заповнюємо форму
    if (data.poll) {
      existingPollId.value = data.poll.id
      showPoll.value       = true
      pollData.value       = {
        question:    data.poll.question,
        options:     data.poll.options.map(o => o.text),
        is_multiple: data.poll.is_multiple,
      }
    }

    // Перевіряємо чернетку після завантаження поста
    const draft = loadDraft()
    if (draft?.title || draft?.content) {
      hasSavedDraft.value = true
      draftSavedAt.value  = draft.savedAt || ''
    }

    // Запускаємо автосейв тільки після завантаження
    // щоб не зберегти порожню форму одразу
    startAutosave()
  } catch {
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