<template>
  <div v-if="!loading && post" class="max-w-4xl mx-auto">
    <article class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
      <!-- Main Image -->
      <div v-if="post.image" class="aspect-video overflow-hidden cursor-pointer" @click="openLightbox(post.image)">
        <img :src="post.image" :alt="post.title" class="w-full h-full object-cover" />
      </div>

      <!-- Content -->
      <div class="p-6 md:p-8">
        <!-- Category & Date -->
        <div class="flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400 mb-4">
          <RouterLink
            v-if="post.category_info"
            :to="`/categories/${post.category_info.slug}`"
            class="text-blue-600 dark:text-blue-400 hover:underline font-medium"
          >
            {{ post.category_info.name }}
          </RouterLink>
          <span>•</span>
          <time>{{ formatDate(post.published_at || post.created_at) }}</time>
        </div>

        <!-- Title -->
        <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-6 break-words">
          {{ post.title }}
        </h1>

        <!-- Author & Stats -->
        <div class="flex items-center justify-between pb-6 mb-6 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
              <UserCircleIcon class="w-8 h-8 text-gray-500" />
            </div>
            <div>
              <p class="font-medium text-gray-900 dark:text-white">
                {{ post.author_info?.username }}
              </p>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ post.author_info?.fullname }}
              </p>
            </div>
          </div>

          <div class="flex items-center gap-4 text-gray-500 dark:text-gray-400">
            <div class="flex items-center gap-1">
              <EyeIcon class="w-5 h-5" />
              <span>{{ post.views_count }}</span>
            </div>
            <div class="flex items-center gap-1">
              <ChatBubbleLeftIcon class="w-5 h-5" />
              <span>{{ post.comments_count || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- Post Content -->
        <div class="prose dark:text-white max-w-none mb-8">
          <div 
            v-html="post.content" 
            class="whitespace-pre-wrap break-words overflow-wrap-anywhere"
            style="word-break: break-word; overflow-wrap: anywhere;"
          ></div>
        </div>

        <!-- Additional Images (clickable gallery) -->
        <div v-if="post.images && post.images.length" class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
          <div
            v-for="(img, index) in post.images"
            :key="img.id"
            class="relative overflow-hidden rounded-lg cursor-pointer group"
            @click="openLightbox(img.image)"
          >
            <img
              :src="img.image"
              alt="Додаткове зображення"
              class="w-full h-48 object-cover transition-transform duration-300 group-hover:scale-105"
            />
            <!-- Оверлей з темнішим фоном + біла іконка в центрі з тінню для кращої видимості -->
            <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <div class="absolute inset-0 bg-black bg-opacity-50"></div>
              <div class="relative z-10 p-4">
                <svg class="w-16 h-16 text-white drop-shadow-lg" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Additional Videos -->
        <div v-if="post.videos && post.videos.length" class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div
            v-for="video in post.videos"
            :key="video.id"
            class="relative rounded-lg overflow-hidden bg-black"
          >
            <video
              :src="video.video"
              controls
              class="w-full aspect-video"
              preload="metadata"
            >
              Ваш браузер не підтримує відео.
            </video>
          </div>
        </div>

        <!-- Tags -->
        <div v-if="post.tags && post.tags.length" class="flex flex-wrap gap-2 mb-8">
          <RouterLink
            v-for="tag in post.tags"
            :key="tag"
            :to="`/posts?tag=${tag}`"
            class="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-1 rounded-lg text-sm hover:bg-gray-200 dark:hover:bg-gray-600 break-words"
          >
            #{{ tag }}
          </RouterLink>
        </div>

        <!-- Edit/Delete Buttons for Author -->
        <div v-if="isAuthor" class="flex flex-col sm:flex-row gap-3 pt-6 border-t border-gray-200 dark:border-gray-700">
          <RouterLink
            :to="`/profile/edit-post/${post.slug}`"
            class="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-center font-medium"
          >
            Редагувати
          </RouterLink>
          
          <button
            @click="deletePost(post.slug)"
            class="px-6 py-2.5 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium"
          >
            Видалити
          </button>
        </div>
      </div>
    </article>

    <!-- Comments Section -->
    <div class="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        Коментарі ({{ post.comments_count || 0 }})
      </h2>
      <p class="text-gray-600 dark:text-gray-400">Коментарі будуть доступні незабаром...</p>
    </div>

    <!-- Lightbox Modal -->
    <Teleport to="body">
      <div
        v-if="lightboxOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-90 p-4"
        @click="closeLightbox"
      >
        <div class="relative max-w-5xl max-h-full">
          <img
            :src="lightboxImage"
            alt="Повний розмір"
            class="max-w-full max-h-full object-contain"
          />
          <button
            class="absolute top-4 right-4 text-white bg-black bg-opacity-50 rounded-full p-2 hover:bg-opacity-70 transition"
            @click.stop="closeLightbox"
          >
            <XMarkIcon class="w-8 h-8" />
          </button>
        </div>
      </div>
    </Teleport>
  </div>

  <!-- Loading -->
  <div v-else-if="loading" class="text-center py-12">
    <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
  </div>

  <!-- Not Found -->
  <div v-else class="text-center py-12">
    <p class="text-gray-600 dark:text-gray-400">Пост не знайдено</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import { postsAPI } from '@/services/api'
import { UserCircleIcon, EyeIcon, ChatBubbleLeftIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { format } from 'date-fns'
import { uk } from 'date-fns/locale'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const loading = ref(true)
const toast = useToast()

// Lightbox state
const lightboxOpen = ref(false)
const lightboxImage = ref('')

const authStore = useAuthStore()

// Перевірка чи користувач є автором
const isAuthor = computed(() => {
  if (!post.value || !authStore.user) return false
  
  // Перевіряємо різні варіанти
  const postAuthorId = post.value.author_info?.id || post.value.author
  const currentUserId = authStore.user?.id || authStore.user?.pk
  
  const postAuthorUsername = post.value.author_info?.username
  const currentUsername = authStore.user?.username || authStore.currentUsername
  
  // Перевірка по ID або по username
  return postAuthorId === currentUserId || postAuthorUsername === currentUsername
})

const deletePost = async (slug) => {
  if (!confirm('Ви впевнені, що хочете видалити цей пост?')) return
  
  try {
    await postsAPI.delete(slug)
    toast.success('Пост успішно видалено')
    router.push('/profile/my-posts')
  } catch (error) {
    console.error('Error deleting post:', error)
    toast.error('Помилка при видаленні посту')
  }
}

const openLightbox = (src) => {
  lightboxImage.value = src
  lightboxOpen.value = true
  document.body.style.overflow = 'hidden' // блок скролу фону
}

const closeLightbox = () => {
  lightboxOpen.value = false
  lightboxImage.value = ''
  document.body.style.overflow = ''
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  try {
    return format(new Date(dateString), 'd MMMM yyyy, HH:mm', { locale: uk })
  } catch {
    return dateString
  }
}

const fetchPost = async () => {
  try {
    loading.value = true
    const { data } = await postsAPI.getBySlug(route.params.slug)
    post.value = data
  } catch (error) {
    console.error('Error fetching post:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchPost()
})
</script>

<style scoped>
.prose {
  word-break: break-word;
  overflow-wrap: anywhere;
}

.prose :deep(*) {
  word-break: break-word;
  overflow-wrap: anywhere;
}

/* Плавна анімація для лайтбоксу */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>