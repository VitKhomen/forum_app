<template>
  <div class="space-y-6">
    <!-- Заголовок -->
    <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
      Коментарі ({{ totalComments }})
    </h2>

    <!-- Форма коментаря -->
    <CommentForm
      :key="`main-form-${formKey}`"
      :post-id="postId"
      :is-authenticated="isAuthenticated"
      :loading="submitting"
      :reply-to="replyingTo"
      :edit-comment="editingComment"
      @submit="handleSubmit"
      @cancel="handleCancel"
    />

    <!-- Список коментарів -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Завантаження...</p>
    </div>

    <div v-else-if="!comments.length" class="text-center py-12 bg-gray-50 dark:bg-gray-900 rounded-lg">
      <p class="text-gray-600 dark:text-gray-400 text-lg mb-2">Коментарів поки немає</p>
      <p class="text-gray-500 dark:text-gray-500 text-sm">Будьте першим!</p>
    </div>

    <div v-else class="space-y-4 mt-6">
      <div v-for="comment in comments" :key="`comment-${comment.id}-${comment.updated_at}`">
        <CommentItem
          :comment="comment"
          :current-user-id="currentUserId"
          :show-replies="showRepliesFor === comment.id"
          @reply="handleReply"
          @edit="handleEdit"
          @delete="handleDelete"
          @toggle-replies="toggleReplies(comment.id)"
        />

        <!-- Розгорнуті відповіді -->
        <Transition name="slide-fade">
          <div v-if="showRepliesFor === comment.id" class="ml-12 mt-4 space-y-4">
            <!-- Форма відповіді -->
            <CommentForm
              v-if="replyingTo?.id === comment.id"
              :key="`reply-form-${comment.id}-${formKey}`"
              :post-id="postId"
              :reply-to="replyingTo"
              :is-authenticated="isAuthenticated"
              :loading="submitting"
              @submit="handleSubmit"
              @cancel="cancelReply"
            />

            <!-- Завантаження -->
            <div v-if="loadingReplies[comment.id]" class="text-center py-4">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
            </div>

            <!-- Список відповідей -->
            <div v-else-if="replies[comment.id]?.length" class="space-y-3">
              <CommentItem
                v-for="reply in replies[comment.id]"
                :key="`reply-${reply.id}-${reply.updated_at}`"
                :comment="reply"
                :current-user-id="currentUserId"
                :is-reply="true"
                @edit="handleEdit"
                @delete="handleDelete"
              />
            </div>

            <div v-else class="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">
              Поки немає відповідей
            </div>
          </div>
        </Transition>
      </div>
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
  postId: { type: Number, required: true },
  postSlug: { type: String, required: true }
})

const emit = defineEmits(['update-comments-count'])

const authStore = useAuthStore()
const toast = useToast()

const comments = ref([])
const replies = ref({})
const loading = ref(false)
const submitting = ref(false)
const loadingReplies = ref({})
const replyingTo = ref(null)
const editingComment = ref(null)
const showRepliesFor = ref(null)
const formKey = ref(0)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentUserId = computed(() => authStore.user?.id)

// Рекурсивний підрахунок (з урахуванням вже завантажених відповідей)
const totalComments = computed(() => {
  if (!Array.isArray(comments.value)) return 0

  const countWithDescendants = (comment) => {
    let count = 1 + (comment.replies_count || 0)

    if (showRepliesFor.value === comment.id && Array.isArray(replies.value[comment.id])) {
      count = 1
      replies.value[comment.id].forEach(reply => {
        count += countWithDescendants(reply)
      })
    }

    return count
  }

  return comments.value.reduce((sum, c) => sum + countWithDescendants(c), 0)
})

watch(totalComments, newCount => emit('update-comments-count', newCount), { immediate: true })

// Завантаження головних коментарів
const fetchComments = async () => {
  loading.value = true
  try {
    const { data } = await commentsAPI.getByPost(props.postId)
    comments.value = data?.results?.comments || data?.comments || data || []
  } catch (error) {
    console.error('Помилка завантаження коментарів:', error)
    toast.error('Не вдалося завантажити коментарі')
  } finally {
    loading.value = false
  }
}

// Завантаження відповідей
const loadReplies = async (commentId) => {
  const id = Number(commentId)
  if (replies.value[id]) return

  loadingReplies.value[id] = true
  try {
    const { data } = await commentsAPI.getReplies(id)
    replies.value[id] = data?.results?.replies || data?.replies || []
  } catch (error) {
    console.error('Помилка завантаження відповідей:', error)
    replies.value[id] = []
  } finally {
    loadingReplies.value[id] = false
  }
}

const toggleReplies = (commentId) => {
  if (showRepliesFor.value === commentId) {
    showRepliesFor.value = null
    replyingTo.value = null
  } else {
    showRepliesFor.value = commentId
    loadReplies(commentId)
  }
}

const handleReply = (comment) => {
  replyingTo.value = comment
  editingComment.value = null
  if (showRepliesFor.value !== comment.id) toggleReplies(comment.id)
}

const cancelReply = () => replyingTo.value = null

const handleEdit = (comment) => {
  editingComment.value = comment
  replyingTo.value = null
}

const handleCancel = () => {
  replyingTo.value = null
  editingComment.value = null
}

const handleSubmit = async (payload) => {
  if (!isAuthenticated.value) return toast.error('Увійдіть, щоб коментувати')

  submitting.value = true
  try {
    if (payload.id) {
      // Редагування
      const { data: updated } = await commentsAPI.update(payload.id, payload.data)

      // Оновлюємо локально
      const updateLocal = (arr) => {
        const idx = arr.findIndex(c => c.id === payload.id)
        if (idx !== -1) arr[idx] = { ...arr[idx], ...updated }
      }

      updateLocal(comments.value)
      Object.values(replies.value).forEach(updateLocal)

      toast.success('Коментар оновлено')
      editingComment.value = null
    } else {
      // Створення
      const { data: newComment } = await commentsAPI.create({
        post: props.postId,
        content: payload.content,
        parent: replyingTo.value?.id || null
      })

      if (replyingTo.value) {
        const pid = replyingTo.value.id
        replies.value[pid] = replies.value[pid] || []
        replies.value[pid].push(newComment)
        const parent = comments.value.find(c => c.id === pid)
        if (parent) parent.replies_count = (parent.replies_count || 0) + 1
        toast.success('Відповідь додано')
        replyingTo.value = null
      } else {
        comments.value.unshift(newComment)
        toast.success('Коментар додано')
      }

      formKey.value++
    }
  } catch (error) {
    toast.error('Помилка при збереженні коментаря')
    console.error(error)
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (commentId) => {
  if (!confirm('Видалити коментар?')) return

  try {
    await commentsAPI.delete(commentId)
    toast.success('Коментар видалено')

    // Видаляємо з головних
    const mIdx = comments.value.findIndex(c => c.id === commentId)
    if (mIdx !== -1) {
      comments.value.splice(mIdx, 1)
      delete replies.value[commentId]
      return
    }

    // Видаляємо з відповідей
    Object.keys(replies.value).forEach(pid => {
      const rIdx = replies.value[pid].findIndex(r => r.id === commentId)
      if (rIdx !== -1) {
        replies.value[pid].splice(rIdx, 1)
        const parent = comments.value.find(c => c.id === Number(pid))
        if (parent && parent.replies_count > 0) parent.replies_count--
        if (replies.value[commentId]) delete replies.value[commentId]
      }
    })
  } catch (error) {
    toast.error('Помилка видалення')
    console.error(error)
  }
}

onMounted(fetchComments)
</script>

<style scoped>
.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.3s ease; }
.slide-fade-enter-from, .slide-fade-leave-to { opacity: 0; transform: translateY(-10px); }
</style>