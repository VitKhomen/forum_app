<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white">
        Коментарі ({{ totalComments }})
      </h2>
    </div>

    <!-- Comment Form -->
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

    <!-- Comments List -->
    <div v-if="!loading && comments.length" class="space-y-4 mt-6">
      <div v-for="comment in comments" :key="comment.id">
        <!-- Main Comment -->
        <CommentItem
          :comment="comment"
          :current-user-id="currentUserId"
          :show-replies="showRepliesFor === comment.id"
          @reply="handleReply"
          @edit="handleEdit"
          @delete="handleDelete"
          @toggle-replies="toggleReplies(comment.id)"
        />

        <!-- Replies -->
        <Transition name="slide-fade">
          <div v-if="showRepliesFor === comment.id" class="ml-12 mt-4 space-y-4">
            <!-- Reply Form -->
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

            <!-- Loading Replies -->
            <div v-if="loadingReplies[comment.id]" class="text-center py-4">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-300 border-t-blue-600"></div>
            </div>

            <!-- Replies List -->
            <div v-else-if="replies[comment.id]?.length" class="space-y-3">
              <CommentItem
                v-for="reply in replies[comment.id]"
                :key="reply.id"
                :comment="reply"
                :current-user-id="currentUserId"
                :is-reply="true"
                @edit="handleEdit"
                @delete="handleDelete"
              />
            </div>

            <!-- No Replies -->
            <div v-else class="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">
              Поки немає відповідей
            </div>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-blue-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Завантаження коментарів...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="!comments.length" class="text-center py-12 bg-gray-50 dark:bg-gray-900 rounded-lg">
      <p class="text-gray-600 dark:text-gray-400 text-lg mb-2">Коментарів поки немає</p>
      <p class="text-gray-500 dark:text-gray-500 text-sm">
        Станьте першим, хто прокоментує цей пост!
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { commentsAPI } from '@/services/api'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import CommentItem from './CommentItem.vue'
import CommentForm from './CommentForm.vue'

const props = defineProps({
  postId: {
    type: Number,
    required: true
  },
  postSlug: {
    type: String,
    required: true
  }
})

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
const formKey = ref(0) // Додано для перемонтування форми

const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentUserId = computed(() => authStore.user?.id)
const totalComments = computed(() => {
  if (!Array.isArray(comments.value)) {
    return 0
  }
  let total = comments.value.length
  Object.values(replies.value).forEach(replyArray => {
    if (Array.isArray(replyArray)) {
      total += replyArray.length
    }
  })
  return total
})

const fetchComments = async () => {
  try {
    loading.value = true
    const { data } = await commentsAPI.getByPost(props.postId)
    
    if (data.results?.comments) {
      comments.value = data.results.comments
    } else if (data.comments) {
      comments.value = data.comments
    } else if (data.results && Array.isArray(data.results)) {
      comments.value = data.results
    } else if (Array.isArray(data)) {
      comments.value = data
    } else {
      comments.value = []
    }
    
  } catch (error) {
    console.error('Error fetching comments:', error)
    toast.error('Помилка завантаження коментарів')
  } finally {
    loading.value = false
  }
}

const loadReplies = async (commentId) => {
  const id = Number(commentId)
  if (replies.value[id]) {
    return
  }

  try {
    loadingReplies.value[id] = true
    const { data } = await commentsAPI.getReplies(id)
    
    let replyData = []
    if (data.results && data.results.replies) {
      replyData = data.results.replies
    } else if (data.replies) {
      replyData = data.replies
    }
    
    if (Array.isArray(replyData)) {
      replies.value[id] = replyData
    } else {
      console.warn('replies НЕ знайдено або не масив!')
      replies.value[id] = []
    }
  } catch (error) {
    console.error('Помилка:', error)
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
  
  if (showRepliesFor.value !== comment.id) {
    showRepliesFor.value = comment.id
    loadReplies(comment.id)
  }
}

const cancelReply = () => {
  replyingTo.value = null
}

const handleEdit = (comment) => {
  editingComment.value = comment
  replyingTo.value = null
}

const handleCancel = () => {
  replyingTo.value = null
  editingComment.value = null
}

const handleSubmit = async (data) => {
  if (!isAuthenticated.value) {
    toast.error('Потрібно увійти в систему')
    return
  }

  if (!authStore.user?.id) {
    toast.error('Помилка авторизації: не знайдено ID користувача')
    return
  }

  try {
    submitting.value = true

    let response

    if (data.id) {
      // Редагування
      response = await commentsAPI.update(data.id, data.data)
      toast.success('Коментар оновлено')
      editingComment.value = null

      const commentIndex = comments.value.findIndex(c => c.id === data.id)
      if (commentIndex !== -1) {
        comments.value[commentIndex].content = data.data.content
      } else {
        Object.keys(replies.value).forEach(parentId => {
          const replyIndex = replies.value[parentId].findIndex(r => r.id === data.id)
          if (replyIndex !== -1) {
            replies.value[parentId][replyIndex].content = data.data.content
          }
        })
      }
    } else {
      // Створення нового
      response = await commentsAPI.create(data)
      toast.success(data.parent ? 'Відповідь додано!' : 'Коментар додано')

      const newComment = {
        ...response.data,
        author_info: {
          id: authStore.user.id,
          username: authStore.user.username,
          full_name: authStore.user.full_name || authStore.user.username,
          avatar: authStore.user.avatar || null
        },
        replies_count: 0
      }

      if (data.parent) {
        const parentId = Number(data.parent)

        if (!replies.value[parentId]) {
          replies.value[parentId] = []
        }

        replies.value[parentId].push(newComment)

        const parent = comments.value.find(c => c.id === parentId)
        if (parent) {
          parent.replies_count = (parent.replies_count || 0) + 1
        }

        replyingTo.value = null
      } else {
        if (!Array.isArray(comments.value)) {
          comments.value = []
        }
        comments.value.unshift(newComment)
      }
      
      // Перемонтовуємо форму для очистки
      formKey.value++
    }
  } catch (error) {
    console.error('Помилка при відправці коментаря:', error)
    const errorMsg = error.response?.data?.detail ||
                     error.response?.data?.message ||
                     error.message ||
                     'Не вдалося відправити коментар'
    toast.error(errorMsg)
  } finally {
    submitting.value = false
    // ВИДАЛЕНО: content.value = '' -ця змінна тут не існує!
    // Форма очиститься сама через свій внутрішній watch
  }
}

const handleDelete = async (commentId) => {
  if (!confirm('Ви впевнені, що хочете видалити цей коментар?')) {
    return
  }

  try {
    await commentsAPI.delete(commentId)
    toast.success('Коментар видалено')
    
    const mainIndex = comments.value.findIndex(c => c.id === commentId)
    if (mainIndex !== -1) {
      comments.value.splice(mainIndex, 1)
    } else {
      Object.keys(replies.value).forEach(parentId => {
        const replyIndex = replies.value[parentId].findIndex(r => r.id === commentId)
        if (replyIndex !== -1) {
          replies.value[parentId].splice(replyIndex, 1)
          
          const parentComment = comments.value.find(c => c.id === parseInt(parentId))
          if (parentComment && parentComment.replies_count > 0) {
            parentComment.replies_count -= 1
          }
        }
      })
    }
  } catch (error) {
    console.error('Error deleting comment:', error)
    toast.error('Помилка видалення коментаря')
  }
}

onMounted(() => {
  fetchComments()
})
</script>

<style scoped>
.slide-fade-enter-active {
  transition: all 0.3s ease;
}

.slide-fade-leave-active {
  transition: all 0.2s ease;
}

.slide-fade-enter-from {
  transform: translateY(-10px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>