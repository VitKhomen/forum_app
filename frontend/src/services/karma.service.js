import { karmaAPI } from '@/services/api'

export default {
  // Моя карма
  async getMyKarma() {
    const response = await karmaAPI.getMyKarma()
    return response.data
  },

  // Історія моєї карми
  async getMyKarmaHistory(options = {}) {
    const { limit = 10, page = 1 } = options
    const response = await karmaAPI.getMyKarmaHistory({ limit, page })
    return response.data.recent_history || []
  },

  // Історія карми користувача
  async getUserKarmaHistory(username, options = {}) {
    const { limit = 10, page = 1 } = options
    const response = await karmaAPI.getUserKarmaHistory(username, { limit, page })
    return response.data.recent_history || []
  },

  // Leaderboard
  async getLeaderboard(limit = 10) {
    const response = await karmaAPI.getLeaderboard({ page_size: limit })
    return response.data
  }
}