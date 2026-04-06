<template>
  <div class="space-y-6">
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
      Коментарі ({{ totalCount }})
    </h2>

    <!-- Головна форма -->
    <CommentForm
      :key="`main-${formKey}`"
      :post-id="postId"
      :is-authenticated="isAuthenticated"
      :loading="submitting"
      :edit-comment="editingComment"
      @submit="handleSubmit"
      @cancel="editingComment = null"
    />

    <!-- Початкове завантаження -->
    <div v-if="loading && !items.length" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600" />
      <p class="mt-4 text-gray-600 dark:text-gray-400">Завантаження...</p>
    </div>

    <!-- Порожній стан -->
    <div
      v-else-if="!items.length && !loading"
      class="text-center py-12 bg-gray-50 dark:bg-gray-900 rounded-lg"
    >
      <p class="text-gray-600 dark:text-gray-400 text-lg mb-2">Коментарів поки немає</p>
      <p class="text-gray-500 dark:text-gray-500 text-sm">Будьте першим!</p>
    </div>

    <!-- Список коментарів -->
    <div v-else class="space-y-4">
      <CommentItem
        v-for="comment in tree"
        :key="`root-${comment.id}`"
        :comment="comment"
        :post-id="postId"
        :current-user-id="currentUserId"
        :is-authenticated="isAuthenticated"
        :depth="0"
        @edit="handleEdit"
        @delete="handleDelete"
        @new-reply="handleNewReply"
      />
    </div>

    <!-- Тригер інфініті скролінгу -->
    <div ref="triggerEl" class="py-4 flex justify-center min-h-[40px]">
      <div
        v-if="loading && items.length"
        class="animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"
      />
      <p
        v-else-if="!hasMore && items.length > 20"
        class="text-sm text-gray-400 dark:text-gray-500"
      >
        Всі коментарі завантажені ✓
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { commentsAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import { useInfiniteScroll } from '@/composables/useInfiniteScroll'
import CommentItem from './CommentItem.vue'
import CommentForm from './CommentForm.vue'

const props = defineProps({
  postId:   { type: Number, required: true },
  postSlug: { type: String, required: true },
})
const emit = defineEmits(['update-comments-count'])

const authStore = useAuthStore()
const toast     = useToast()

const submitting     = ref(false)
const editingComment = ref(null)
const formKey        = ref(0)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentUserId   = computed(() => authStore.user?.id)

// ── Інфініті скролінг ────────────────────────────────────────

const fetchPage = (params) =>
  commentsAPI.getByPost(props.postId, {
    ...params,
    page_size: 20,
    ordering: 'created_at',
  })

const {
  items,
  loading,
  hasMore,
  totalCount,
  triggerEl,
  reset,
} = useInfiniteScroll(fetchPage)

// Повідомляємо батька про зміну кількості
watch(totalCount, (n) => emit('update-comments-count', n))

// ── Дерево з плоского списку ─────────────────────────────────

const tree = computed(() => {
  const map   = {}
  const roots = []

  items.value.forEach((c) => {
    map[c.id] = { ...c, children: [] }
  })

  items.value.forEach((c) => {
    if (c.parent && map[c.parent]) {
      map[c.parent].children.push(map[c.id])
    } else {
      roots.push(map[c.id])
    }
  })

  return roots
})

// ── Дії ──────────────────────────────────────────────────────

const handleSubmit = async (payload) => {
  if (!isAuthenticated.value) return toast.error('Увійдіть, щоб коментувати')
  submitting.value = true
  try {
    if (payload.id) {
      // Редагування
      const { data: updated } = await commentsAPI.update(payload.id, payload.data)
      const idx = items.value.findIndex((c) => c.id === payload.id)
      if (idx !== -1) items.value[idx] = { ...items.value[idx], ...updated }
      toast.success('Коментар оновлено')
      editingComment.value = null
    } else {
      // Новий коментар
      const { data: newComment } = await commentsAPI.create({
        post:    props.postId,
        content: payload.content,
        parent:  null,
      })
      items.value.unshift({ ...newComment, children: [] })
      totalCount.value++
      toast.success('Коментар додано')
      formKey.value++
    }
  } catch {
    toast.error('Помилка при збереженні')
  } finally {
    submitting.value = false
  }
}

const handleNewReply = ({ reply }) => {
  items.value.push({ ...reply, children: [] })
  totalCount.value++
}

const handleEdit = (comment) => {
  editingComment.value = comment
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const handleDelete = async (commentId) => {
  if (!confirm('Видалити коментар і всі відповіді?')) return
  try {
    await commentsAPI.delete(commentId)
    toast.success('Коментар видалено')

    // Збираємо id коментаря + всіх нащадків
    const toRemove = new Set([commentId])
    let changed = true
    while (changed) {
      changed = false
      items.value.forEach((c) => {
        if (c.parent && toRemove.has(c.parent) && !toRemove.has(c.id)) {
          toRemove.add(c.id)
          changed = true
        }
      })
    }

    totalCount.value = Math.max(0, totalCount.value - toRemove.size)
    items.value = items.value.filter((c) => !toRemove.has(c.id))
  } catch {
    toast.error('Помилка видалення')
  }
}
</script>