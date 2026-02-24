import axios from 'axios'
import Cookies from 'js-cookie'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    // 'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = Cookies.get('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // Якщо дані це FormData, видаляємо Content-Type 
    // щоб браузер сам встановив правильний з boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const refreshToken = Cookies.get('refresh_token')
      
      if (!refreshToken) {
        return Promise.reject(error)
      }
      
      try {
        const { data } = await axios.post(
          `${api.defaults.baseURL}/auth/token/refresh/`,
          { refresh: refreshToken }
        )
        
        Cookies.set('access_token', data.access)
        api.defaults.headers.Authorization = `Bearer ${data.access}`
        
        return api(originalRequest)
      } catch (refreshError) {
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }
    
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register/', data),
  login: (data) => api.post('/auth/login/', data),
  logout: (refreshToken) => api.post('/auth/logout/', { refresh_token: refreshToken }),
  getProfile: () => api.get('/auth/profile/'),
  updateProfile: (data) => {
    // Якщо data це FormData або містить файли, не встановлюємо Content-Type
    return api.patch('/auth/profile/', data)
  },
  changePassword: (data) => api.post('/auth/change-password/', data),
}

// Posts API
export const postsAPI = {
  getAll: (params) => api.get('/posts/', { params }),
  getBySlug: (slug) => api.get(`/posts/${slug}/`),
  create: (data) => api.post('/posts/', data),
  update: (slug, data) => api.patch(`/posts/${slug}/`, data),
  delete: (slug) => api.delete(`/posts/${slug}/`),
  getMy: (params) => api.get('/posts/my/', { params }),
  getByTag: (tag, params) => api.get('/posts/by_tag/', { params: { tag, ...params } }),
  getPopular: (params) => api.get('/posts/popular/', { params }),
  getTrending: (params) => api.get('/posts/trending/', { params }),
  getById: (id) => api.get(`/posts/${id}/`),
  
  // Методи для роботи з додатковими зображеннями
  addImages: (slug, formData) => {
    return api.post(`/posts/${slug}/images/`, formData)
  },
  
  bulkDeleteImages: (slug, imageIds) => {
    return api.delete(`/posts/${slug}/images/bulk_delete/`, {
      data: { ids: imageIds }  // ← передаємо масив у body
    })
  },
  
  // Методи для роботи з відео
  addVideos: (slug, formData) => {
    return api.post(`/posts/${slug}/videos/`, formData)
  },
  
  bulkDeleteVideos: (slug, videoIds) => {
    return api.delete(`/posts/${slug}/videos/bulk_delete/`, {
      data: { ids: videoIds }
    })
  },
}

// Categories API
export const categoriesAPI = {
  getAll: (params) => api.get('/categories/', { params }),
  getBySlug: (slug) => api.get(`/categories/${slug}/`),
}

// Comments API
export const commentsAPI = {
  getAll: (params) => api.get('/comments/', { params }),
  getByPost: (postId, params) => api.get(`/comments/post/${postId}/`, { params }),
  create: (data) => api.post('/comments/', data),
  update: (id, data) => api.patch(`/comments/${id}/`, data),
  delete: (id) => api.delete(`/comments/${id}/`),
  getMy: (params) => api.get('/comments/my-comments/', { params }),
  getReplies: (commentId, params) => api.get(`/comments/post/${commentId}/replies/`, { params }),
}

// Feedback API
export const feedbackAPI = {
  send: (data) => api.post('/feedback/send/', data),
}

// Likes API
export const likesAPI = {
  toggle: (contentType, objectId) => api.post('/likes/toggle/', {
    content_type: contentType,
    object_id: objectId
  }),
  
  getCount: (contentType, objectId) => api.get('/likes/count/', {
    params: { content_type: contentType, object_id: objectId }
  }),
}

export const karmaAPI = {
  getMyKarma: () => api.get('/karma/my_karma/'),
  getMyKarmaHistory: (params) => api.get('/karma/my_karma/', { params }),
  getUserKarma: (username) => api.get(`/karma/user/${username}/`),
  getUserKarmaHistory: (username, params) => api.get(`/karma/user/${username}/`, { params }),
  getLeaderboard: (params) => api.get('/karma/leaderboard/', { params }),
}

export const moviesAPI = {
  search:   (query, page = 1, mediaType = 'movie') =>
    api.get('/movies/search/', { params: { q: query, page, media_type: mediaType } }),

  getById:  (id, mediaType = 'movie') =>
    api.get(`/movies/${id}/`, { params: { media_type: mediaType } }),

  discover: (params = {}, mediaType = 'movie') =>
    api.get('/movies/discover/', { params: { ...params, media_type: mediaType } }),

  trending: (mediaType = 'movie', timeWindow = 'week') =>
    api.get('/movies/trending/', { params: { media_type: mediaType, time_window: timeWindow } }),

  nowPlaying: (mediaType = 'movie', page = 1) =>
    api.get(`/movies/${mediaType === 'movie' ? 'now_playing' : 'on_the_air'}/`, { params: { page } }),

  topRated: (mediaType = 'movie', page = 1) =>
    api.get('/movies/top_rated/', { params: { page, media_type: mediaType } }),

  popular:  (mediaType = 'movie', page = 1) =>
    api.get('/movies/popular/', { params: { page, media_type: mediaType } }),

  genres:   (mediaType = 'movie') =>
    api.get('/movies/genres/', { params: { media_type: mediaType } }),

  recommendations: (movieId, mediaType = 'movie') =>
    api.get(`/movies/${movieId}/recommendations/`, { params: { media_type: mediaType } }),

  // Watchlist
  toggleWatchlist: (id, mediaType = 'movie') =>
    api.post(`/movies/${id}/watchlist/`, { media_type: mediaType }),
  removeWatchlist: (id, mediaType = 'movie') =>
    api.delete(`/movies/${id}/watchlist/`, { data: { media_type: mediaType } }),
  getMyWatchlist:  (params) => api.get('/movies/me/watchlist/', { params }),

  // Favorites
  toggleFavorite: (id, mediaType = 'movie') =>
    api.post(`/movies/${id}/favorite/`, { media_type: mediaType }),
  removeFavorite: (id, mediaType = 'movie') =>
    api.delete(`/movies/${id}/favorite/`, { data: { media_type: mediaType } }),
  getMyFavorites: (params) => api.get('/movies/me/favorites/', { params }),

  // Ratings
  rateMovie:    (id, rating, mediaType = 'movie', review = '') =>
    api.post(`/movies/${id}/rate/`,   { rating, review, media_type: mediaType }),
  updateRating: (id, rating, mediaType = 'movie', review = '') =>
    api.put(`/movies/${id}/rate/`,    { rating, review, media_type: mediaType }),
  deleteRating: (id, mediaType = 'movie') =>
    api.delete(`/movies/${id}/rate/`, { data: { media_type: mediaType } }),
  getMyRatings: (params) => api.get('/movies/me/ratings/', { params }),  // ← НОВИЙ
}




export default api