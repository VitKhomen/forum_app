// composables/useCommentsSync.js
import { ref } from 'vue'

// Глобальний Map для зберігання кількості коментарів
const commentsCountMap = ref(new Map())

// Event listeners для оновлення
const listeners = new Set()

export function useCommentsSync() {
  const updateCommentsCount = (postId, count) => {
    commentsCountMap.value.set(postId, count)
    
    // Повідомляємо всіх слухачів
    listeners.forEach(callback => callback(postId, count))
  }

  const getCommentsCount = (postId) => {
    return commentsCountMap.value.get(postId)
  }

  const subscribe = (callback) => {
    listeners.add(callback)
    
    // Повертаємо функцію для відписки
    return () => listeners.delete(callback)
  }

  return {
    updateCommentsCount,
    getCommentsCount,
    subscribe
  }
}