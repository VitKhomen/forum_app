// composables/useKarma.js
import { ref, computed } from 'vue'
import karmaService from '@/services/karma.service'

export function useKarma() {
  const myKarma = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // Загрузить мою карму
  const fetchMyKarma = async () => {
    loading.value = true
    error.value = null
    try {
      const data = await karmaService.getMyKarma()
      myKarma.value = data
      return data
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  // Загрузить историю карми
  const getKarmaHistory = async (userId = null, options = {}) => {
    try {
      if (userId) {
        return await karmaService.getUserKarmaHistory(userId, options)
      } else {
        return await karmaService.getMyKarmaHistory(options)
      }
    } catch (err) {
      console.error('Ошибка загрузки истории:', err)
      return []
    }
  }

  // Загрузить leaderboard
  const getLeaderboard = async (limit = 10) => {
    try {
      return await karmaService.getLeaderboard(limit)
    } catch (err) {
      console.error('Ошибка загрузки leaderboard:', err)
      return []
    }
  }

  // Форматирование даты
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'щойно'
    if (diffMins < 60) return `${diffMins} хв тому`
    if (diffHours < 24) return `${diffHours} год тому`
    if (diffDays < 7) return `${diffDays} дн тому`
    
    return date.toLocaleDateString('uk-UA', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Вычислить прогресс до следующего уровня
  const getLevelProgress = (karma) => {
    const currentLevel = Math.floor(karma / 100) + 1
    const karmaInCurrentLevel = karma % 100
    const progressPercent = karmaInCurrentLevel
    const karmaToNextLevel = 100 - karmaInCurrentLevel

    return {
      currentLevel,
      karmaInCurrentLevel,
      progressPercent,
      karmaToNextLevel,
      nextLevel: currentLevel + 1
    }
  }

  // Получить цвет уровня
  const getLevelColor = (level) => {
    if (level >= 10) return '#9333ea' // purple
    if (level >= 5) return '#dc2626'  // red
    if (level >= 3) return '#ea580c'  // orange
    return '#16a34a' // green
  }

  return {
    // State
    myKarma,
    loading,
    error,

    // Methods
    fetchMyKarma,
    getKarmaHistory,
    getLeaderboard,
    formatDate,
    getLevelProgress,
    getLevelColor
  }
}