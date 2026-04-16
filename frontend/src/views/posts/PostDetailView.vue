<template>
  <div v-if="!isPageLoading && post" class="grid cols-1 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
    <!-- Основний контент (2/3 на lg+) -->
    <div class="lg:col-span-2">
      <article class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
        <!-- Main Image - клікабельна -->
        <div 
          v-if="post.image" 
          class="cursor-pointer overflow-hidden"
          @click="openLightbox(0)"
        >
          <img
            :src="post.image"
            :alt="post.title"
            class="w-full h-auto max-h-[70vh] mx-auto object-contain"
          />
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

          <!-- Author -->
          <div class="flex items-center justify-between pb-6 mb-6">
            <div class="flex items-start gap-3">
              <!-- Avatar -->
              <div class="w-20 h-20 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden flex-shrink-0">
                <img
                  v-if="post.author_info?.avatar"
                  :src="post.author_info.avatar"
                  :alt="post.author_info.username"
                  class="w-full h-full object-cover"
                />
                <UserCircleIcon v-else class="w-full h-full text-gray-500" />
              </div>
              
              <div>
                <AuthorWithKarma
                  size="lg"
                  :username="post.author_info?.username"
                  :karma="post.author_karma_points || 0"
                  :level="post.author_karma_level || 1"
                />
              </div>
            </div>

          </div>
          
          <!-- Post Content -->
          <template v-if="post.content && post.content.trim()">
            <div class="border-b border-gray-200 dark:border-gray-700 my-8"></div>
            
            <div class="prose dark:prose-invert max-w-none mb-8">
              <div 
                v-html="sanitize(post.content)" 
                class="whitespace-pre-wrap break-words overflow-wrap-anywhere"
                style="word-break: break-word; overflow-wrap: anywhere;"
              ></div>
            </div>
          </template>
          
          
          <!-- Additional Images (clickable gallery) -->
          <template v-if="post.images && post.images.length">
            <div class="border-b border-gray-200 dark:border-gray-700 my-8"></div>
            
            <div class="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
              <div
                v-for="(img, idx) in post.images"
                :key="img.id"
                class="relative overflow-hidden rounded-lg cursor-pointer group aspect-square"
                @click="openLightbox(idx + 1)"
              >
                <img
                  :src="img.image"
                  alt="Додаткове зображення"
                  class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
                <!-- Оверлей для збільшення -->
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
          </template>
          
          <!-- Additional Videos -->
          <template v-if="post.videos && post.videos.length">
            <div class="border-b border-gray-200 dark:border-gray-700 my-8"></div>
            
            <div class="space-y-6 mb-8">
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
          </template>
      
      <!-- Tags + Stats -->
      <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <!-- Теги + статистика в одному рядку, але на мобілках вертикально -->
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <!-- Теги -->
          <div v-if="post.tags && post.tags.length" class="flex flex-wrap gap-2">
            <RouterLink
              v-for="tag in post.tags"
              :key="tag"
              :to="`/posts?tag=${tag}`"
              class="bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 px-3 py-1 rounded-lg text-sm hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
            >
              #{{ tag }}
            </RouterLink>
          </div>

          <!-- Статистика (зліва на мобілках, праворуч на десктопі) -->
          <div class="flex items-center gap-6 text-sm text-gray-500 dark:text-gray-400">
            <div class="flex items-center gap-1.5">
              <EyeIcon class="w-5 h-5" />
              <span>{{ post.views_count || 0 }}</span>
            </div>

            <div class="flex items-center gap-1.5">
              <ChatBubbleLeftIcon class="w-5 h-5" />
              <span>{{ commentsCount }}</span>
            </div>

            <div @click.stop>
              <LikeButton
                content-type="post"
                size="md"
                :object-id="post.id"
                :initial-likes-count="post.likes_count || 0"
                :initial-is-liked="post.is_liked || false"
              />
            </div>
            <BookmarkButton
              :post-id="post.id"
              :initial-bookmarked="post.is_bookmarked || false"
              size="md"
            />
          </div>
        </div>
      </div>
    
      <!-- Edit/Delete Buttons for Author -->
      <div v-if="isAuthor" class="flex flex-col sm:flex-row gap-3 pt-6">
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
      <CommentsSection 
        :post-id="post.id" 
        :post-slug="post.slug"
        @update-comments-count="updateCommentsCount"
      />    
    </div> 
      
    <!-- Сайдбар (1/3 на lg+) -->
    <aside class="lg:col-span-1">
      <div class="sticky top-20 space-y-6">
        <PopularSidebar :tags="popularTags" :posts="popularPosts" />
      </div>
    </aside>

    <!-- Lightbox Modal -->
    <Teleport to="body">
      <div
        v-if="lightboxOpen"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-90"
        @click="closeLightbox"
      >
        <div class="relative w-full h-full flex items-center justify-center p-4 md:p-8">
          <!-- Стрілка вліво -->
          <button
            v-if="galleryImages.length > 1"
            class="absolute left-4 md:left-12 text-white text-5xl hover:text-gray-300 transition z-10"
            @click.stop="prevImage"
          >
            ←
          </button>

          <!-- Головна картинка -->
          <img
            :src="galleryImages[currentImageIndex]"
            :alt="`Зображення ${currentImageIndex + 1} з ${galleryImages.length}`"
            class="max-w-full max-h-full object-contain transition-opacity duration-300"
          />

          <!-- Стрілка вправо -->
          <button
            v-if="galleryImages.length > 1"
            class="absolute right-4 md:right-12 text-white text-5xl hover:text-gray-300 transition z-10"
            @click.stop="nextImage"
          >
            →
          </button>

          <!-- Кнопка закриття -->
          <button
            class="absolute top-4 right-4 text-white bg-black bg-opacity-50 rounded-full p-2 hover:bg-opacity-70 transition z-10"
            @click.stop="closeLightbox"
          >
            <XMarkIcon class="w-8 h-8" />
          </button>

          <!-- Індикатор (номер фото) -->
          <div v-if="galleryImages.length > 1" class="absolute bottom-8 text-white text-lg bg-black bg-opacity-50 px-4 py-2 rounded-full">
            {{ currentImageIndex + 1 }} / {{ galleryImages.length }}
          </div>
        </div>
      </div>
    </Teleport>
  </div>

  <!-- Loading Skeleton -->
  <div v-else-if="isPageLoading" class="max-w-7xl mx-auto">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Основний контент (2/3) -->
      <div class="lg:col-span-2 space-y-8">
        <div class="w-full h-72 md:h-96 bg-gray-200 dark:bg-gray-700 rounded-xl animate-pulse" />

        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 md:p-8 space-y-8">
          <div class="flex gap-3">
            <div class="h-4 w-28 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div class="h-4 w-36 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>

          <div class="space-y-4">
            <div class="h-9 w-full bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div class="h-9 w-4/5 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>

          <div class="flex items-center gap-4 pb-6 border-b border-gray-200 dark:border-gray-700">
            <div class="w-16 h-16 rounded-full bg-gray-200 dark:bg-gray-700 animate-pulse" />
            <div class="space-y-3 flex-1">
              <div class="h-5 w-52 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              <div class="h-4 w-32 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            </div>
          </div>

          <div class="space-y-3">
            <div v-for="i in 10" :key="i" 
                class="h-4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse"
                :style="{ width: [100, 95, 100, 60, 100, 85, 100, 70, 100, 55][i-1] + '%' }">
            </div>
          </div>
        </div>

        <!-- Скелетон коментарів -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <div class="h-8 w-48 bg-gray-200 dark:bg-gray-700 rounded mb-6 animate-pulse" />
          <div class="space-y-6">
            <SkeletonLoader v-for="i in 3" :key="i" type="comment" />
          </div>
        </div>
      </div>

      <!-- Сайдбар -->
      <aside class="lg:col-span-1">
        <div class="sticky top-20 space-y-6">
          <SkeletonLoader type="sidebar" />
        </div>
      </aside>
    </div>
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
import PopularSidebar from '@/components/posts/PopularSidebar.vue'
import CommentsSection from '@/components/comments/CommentsSection.vue'
import LikeButton from '@/components/ui/LikeButton.vue'
import { useCommentsSync } from '@/composables/useCommentsSync'
import AuthorWithKarma from '@/components/ui/KarmaBadge.vue'
import BookmarkButton from '@/components/ui/BookmarkButton.vue'
import { sanitize } from '@/utils/sanitize'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'

const route = useRoute()
const router = useRouter()
const post = ref(null)
const toast = useToast()
const popularPosts = ref([])
const popularTags = ref([])

const loadingPost = ref(true)
const loadingPopular = ref(true)
const loadingTags = ref(true)

const authStore = useAuthStore()
const { updateCommentsCount: syncCommentsCount } = useCommentsSync()

// Lightbox state
const lightboxOpen = ref(false)
const galleryImages = ref([])
const currentImageIndex = ref(0)

const commentsCount = ref(0)

// Перевірка чи користувач є автором
const isAuthor = computed(() => {
  if (!post.value || !authStore.user) return false
  
  const postAuthorId = post.value.author_info?.id || post.value.author
  const currentUserId = authStore.user?.id || authStore.user?.pk
  
  const postAuthorUsername = post.value.author_info?.username
  const currentUsername = authStore.user?.username || authStore.currentUsername
  
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

const updateCommentsCount = (count) => {
  commentsCount.value = count
  
  if (post.value?.id) {
    syncCommentsCount(post.value.id, count)
  }
}

// Відкрити лайтбокс
const openLightbox = (index) => {
  galleryImages.value = []
  
  if (post.value.image) {
    galleryImages.value.push(post.value.image)
  }
  
  if (post.value.images && post.value.images.length > 0) {
    post.value.images.forEach(img => {
      galleryImages.value.push(img.image)
    })
  }
  
  currentImageIndex.value = index
  lightboxOpen.value = true
  document.body.style.overflow = 'hidden'
}

const nextImage = () => {
  currentImageIndex.value = (currentImageIndex.value + 1) % galleryImages.value.length
}

const prevImage = () => {
  currentImageIndex.value = (currentImageIndex.value - 1 + galleryImages.value.length) % galleryImages.value.length
}

const closeLightbox = () => {
  lightboxOpen.value = false
  galleryImages.value = []
  currentImageIndex.value = 0
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

const isPageLoading = computed(() => 
  loadingPost.value || loadingPopular.value || loadingTags.value
)

const fetchPost = async () => {
  try {
    loadingPost.value = true
    const { data } = await postsAPI.getBySlug(route.params.slug)
    post.value = data
    commentsCount.value = data.comments_count || 0
  } catch (error) {
    console.error('Error fetching post:', error)
  } finally {
    loadingPost.value = false
  }
}

const CACHE_DURATION = 1000 * 60 * 30 // 30 хвилин

const getCachedData = (key) => {
  const cached = sessionStorage.getItem(key)
  if (!cached) return null

  try {
    const parsed = JSON.parse(cached)
    // Перевіряємо, чи не застарів кеш
    if (parsed.timestamp && Date.now() - parsed.timestamp < CACHE_DURATION) {
      return parsed.data
    }
    // Якщо застарів — видаляємо
    sessionStorage.removeItem(key)
    return null
  } catch {
    sessionStorage.removeItem(key)
    return null
  }
}

const setCache = (key, data) => {
  const cacheObject = {
    data: data,
    timestamp: Date.now()
  }
  sessionStorage.setItem(key, JSON.stringify(cacheObject))
}

// ──────────────────────────────────────

const fetchPopular = async () => {
  const cached = getCachedData('popular_posts')
  if (cached) {
    popularPosts.value = cached
    loadingPopular.value = false
    return
  }

  try {
    loadingPopular.value = true
    const { data } = await postsAPI.getPopular({ limit: 5 })
    popularPosts.value = data.results || data || []

    // Зберігаємо в кеш
    setCache('popular_posts', popularPosts.value)
  } catch (error) {
    console.error('Error fetching popular posts:', error)
    popularPosts.value = []
  } finally {
    loadingPopular.value = false
  }
}

const fetchPopularTags = async () => {
  const cached = getCachedData('popular_tags')
  if (cached) {
    popularTags.value = cached
    loadingTags.value = false
    return
  }

  try {
    loadingTags.value = true
    const { data } = await postsAPI.getAll({ page_size: 50 })
    const posts = data.results || data || []

    const tagsMap = {}
    posts.forEach(p => {
      if (p.tags && Array.isArray(p.tags)) {
        p.tags.forEach(tag => {
          tagsMap[tag] = (tagsMap[tag] || 0) + 1
        })
      }
    })

    popularTags.value = Object.entries(tagsMap)
      .map(([name, count]) => ({ name, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)

    setCache('popular_tags', popularTags.value)
  } catch (error) {
    console.error('Error fetching popular tags:', error)
    popularTags.value = []
  } finally {
    loadingTags.value = false
  }
}

onMounted(() => {
  fetchPost()
  fetchPopular()
  fetchPopularTags()
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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.main-image-container {
  max-height: 80vh;
  overflow: hidden;
}
</style>