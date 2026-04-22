<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Мої пости</h1>
      <RouterLink
        to="/profile/create-post"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Створити новий
      </RouterLink>
    </div>

    <!-- Скелетон -->
    <div v-if="loading" class="space-y-4">
      <div
        v-for="i in 5"
        :key="i"
        class="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
      >
        <div class="flex gap-4 items-start">
          <!-- Зображення скелетон -->
          <div class="w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse flex-shrink-0" />
          <!-- Контент скелетон -->
          <div class="flex-1 space-y-3">
            <div class="h-6 w-3/4 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div class="h-4 w-full bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div class="h-4 w-2/3 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div class="flex gap-4 mt-2">
              <div class="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              <div class="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
              <div class="h-4 w-20 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            </div>
          </div>
          <!-- Кнопки скелетон -->
          <div class="flex flex-col gap-2 flex-shrink-0">
            <div class="h-7 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
            <div class="h-7 w-24 bg-gray-200 dark:bg-gray-700 rounded animate-pulse" />
          </div>
        </div>
      </div>
    </div>

    <!-- Список постів -->
    <div v-else-if="posts.length" class="space-y-4">
      <div
        v-for="post in posts"
        :key="post.id"
        class="bg-white dark:bg-gray-800 rounded-lg shadow p-6"
      >
        <div class="flex gap-4 items-start">
          <!-- Зображення -->
          <RouterLink :to="`/posts/${post.slug}`" class="flex-shrink-0">
            <img
              v-if="post.image"
              :src="post.image"
              :alt="post.title"
              class="w-24 h-24 object-cover rounded-lg hover:scale-105 transition-transform duration-300"
            />
            <div
              v-else
              class="w-24 h-24 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center text-gray-500 dark:text-gray-400 text-xs text-center p-2"
            >
              Без зображення
            </div>
          </RouterLink>

          <!-- Контент -->
          <div class="flex-1 min-w-0">
            <RouterLink
              :to="`/posts/${post.slug}`"
              class="text-xl font-semibold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 block mb-2 break-words"
            >
              {{ post.title }}
            </RouterLink>
            <p class="text-gray-600 dark:text-gray-400 text-sm mt-2 line-clamp-2 break-words">
              {{ post.excerpt }}
            </p>
            <div class="flex flex-wrap items-center gap-4 mt-3 text-sm text-gray-500 dark:text-gray-400">
              <span>👁️ {{ post.views_count }} переглядів</span>
              <span>💬 {{ post.comments_count }} коментарів</span>
              <span
                class="font-medium"
                :class="post.status === 'published'
                  ? 'text-green-600 dark:text-green-400'
                  : 'text-yellow-600 dark:text-yellow-400'"
              >
                {{ post.status === 'published' ? '✓ Опубліковано' : '✎ Чернетка' }}
              </span>
            </div>
          </div>

          <!-- Кнопки -->
          <div class="flex flex-col gap-2 flex-shrink-0">
            <RouterLink
              :to="`/profile/edit-post/${post.slug}`"
              class="px-3 py-1 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm whitespace-nowrap text-center"
            >
              Редагувати
            </RouterLink>
            <button
              @click="deletePost(post.slug)"
              class="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700 text-sm whitespace-nowrap"
            >
              Видалити
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else class="text-center py-12">
      <p class="text-gray-600 dark:text-gray-400 mb-4">У вас ще немає постів</p>
      <RouterLink
        to="/profile/create-post"
        class="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Створити перший пост
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { postsAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

const toast   = useToast()
const posts   = ref([])
const loading = ref(true)

const fetchMyPosts = async () => {
  try {
    loading.value = true
    const { data } = await postsAPI.getMy()
    posts.value = data.results || data
  } catch {
    toast.error('Помилка завантаження постів')
  } finally {
    loading.value = false
  }
}

const deletePost = async (slug) => {
  if (!confirm('Ви впевнені, що хочете видалити цей пост?')) return
  try {
    await postsAPI.delete(slug)
    toast.success('Пост видалено')
    posts.value = posts.value.filter(p => p.slug !== slug)
  } catch {
    toast.error('Помилка видалення')
  }
}

onMounted(fetchMyPosts)
</script>