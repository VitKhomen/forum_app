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

    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Завантаження...</p>
    </div>

    <div v-else-if="!tree.length" class="text-center py-12 bg-gray-50 dark:bg-gray-900 rounded-lg">
      <p class="text-gray-600 dark:text-gray-400 text-lg mb-2">Коментарів поки немає</p>
      <p class="text-gray-500 dark:text-gray-500 text-sm">Будьте першим!</p>
    </div>

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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { commentsAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import CommentItem from './CommentItem.vue'
import CommentForm from './CommentForm.vue'

const props = defineProps({
  postId:   { type: Number, required: true },
  postSlug: { type: String, required: true },
})
const emit = defineEmits(['update-comments-count'])

const authStore = useAuthStore()
const toast = useToast()

const flat        = ref([])   // плоский список всіх коментарів
const loading     = ref(false)
const submitting  = ref(false)
const editingComment = ref(null)
const formKey     = ref(0)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentUserId   = computed(() => authStore.user?.id)

// ── Дерево з плоского списку ─────────────────────────────────
const tree = computed(() => {
  const map = {}
  const roots = []

  flat.value.forEach(c => { map[c.id] = { ...c, children: [] } })

  flat.value.forEach(c => {
    if (c.parent && map[c.parent]) {
      map[c.parent].children.push(map[c.id])
    } else if (!c.parent) {
      roots.push(map[c.id])
    } else {
      // parent існує в БД але не завантажений — показуємо як root
      roots.push(map[c.id])
    }
  })

  return roots
})

const totalCount = computed(() => flat.value.length)
watch(totalCount, n => emit('update-comments-count', n), { immediate: true })

// ── Завантаження ─────────────────────────────────────────────
const fetchComments = async () => {
  loading.value = true
  try {
    const { data } = await commentsAPI.getByPost(props.postId)
    // post_comments тепер повертає плоский список всіх коментарів
    flat.value = data?.comments || data?.results || []
  } catch (error) {
    console.error(error)
    toast.error('Не вдалося завантажити коментарі')
  } finally {
    loading.value = false
  }
}

// ── Новий root-коментар ───────────────────────────────────────
const handleSubmit = async (payload) => {
  if (!isAuthenticated.value) return toast.error('Увійдіть, щоб коментувати')
  submitting.value = true
  try {
    if (payload.id) {
      const { data: updated } = await commentsAPI.update(payload.id, payload.data)
      const idx = flat.value.findIndex(c => c.id === payload.id)
      if (idx !== -1) flat.value[idx] = { ...flat.value[idx], ...updated }
      toast.success('Коментар оновлено')
      editingComment.value = null
    } else {
      const { data: newComment } = await commentsAPI.create({
        post:    props.postId,
        content: payload.content,
        parent:  null,
      })
      newComment.children = []
      flat.value.unshift(newComment)
      toast.success('Коментар додано')
      formKey.value++
    }
  } catch (error) {
    toast.error('Помилка при збереженні')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

// ── Нова відповідь (з CommentItem) ───────────────────────────
const handleNewReply = ({ reply }) => {
  // Просто додаємо в плоский список — дерево перебудується само
  flat.value.push(reply)
}

// ── Редагування ───────────────────────────────────────────────
const handleEdit = (comment) => {
  editingComment.value = comment
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// ── Видалення з усіма нащадками ───────────────────────────────
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
      flat.value.forEach(c => {
        if (c.parent && toRemove.has(c.parent) && !toRemove.has(c.id)) {
          toRemove.add(c.id)
          changed = true
        }
      })
    }
    flat.value = flat.value.filter(c => !toRemove.has(c.id))
  } catch (error) {
    toast.error('Помилка видалення')
    console.error(error)
  }
}

onMounted(fetchComments)
</script>