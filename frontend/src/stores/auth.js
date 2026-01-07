import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import Cookies from 'js-cookie'
import { authAPI } from '@/services/api'
import { useToast } from 'vue-toastification'

const toast = useToast()

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const isStaff = computed(() => user.value?.is_staff || false)

  const setTokens = (access, refresh) => {
    Cookies.set('access_token', access, { expires: 1/24 }) // 1 hour
    Cookies.set('refresh_token', refresh, { expires: 7 }) // 7 days
  }

  const removeTokens = () => {
    Cookies.remove('access_token')
    Cookies.remove('refresh_token')
  }

  const login = async (credentials) => {
    try {
      loading.value = true
      const { data } = await authAPI.login(credentials)
      
      user.value = data.user
      setTokens(data.access, data.refresh)
      
      toast.success('Успішний вхід!')
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || 'Помилка входу'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      loading.value = false
    }
  }

  const register = async (userData) => {
    try {
      loading.value = true
      const { data } = await authAPI.register(userData)
      
      user.value = data.user
      setTokens(data.access, data.refresh)
      
      toast.success('Реєстрація успішна!')
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || 'Помилка реєстрації'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      const refreshToken = Cookies.get('refresh_token')
      if (refreshToken) {
        await authAPI.logout(refreshToken)
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      user.value = null
      removeTokens()
      toast.info('Ви вийшли з системи')
    }
  }

  const fetchProfile = async () => {
    try {
      loading.value = true
      const { data } = await authAPI.getProfile()
      user.value = data
      return { success: true }
    } catch (error) {
      console.error('Fetch profile error:', error)
      removeTokens()
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  const updateProfile = async (profileData) => {
    try {
      loading.value = true
      
      // Якщо profileData це FormData, відправляємо як є
      // Якщо це звичайний об'єкт, конвертуємо в FormData
      let formData = profileData
      
      if (!(profileData instanceof FormData)) {
        formData = new FormData()
        Object.keys(profileData).forEach(key => {
          if (profileData[key] !== null && profileData[key] !== undefined) {
            formData.append(key, profileData[key])
          }
        })
      }
      
      const { data } = await authAPI.updateProfile(formData)
      user.value = data
      toast.success('Профіль оновлено!')
      return { success: true }
    } catch (error) {
      console.error('Update profile error:', error)
      const message = error.response?.data?.detail || 
                     error.response?.data?.message ||
                     'Помилка оновлення'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      loading.value = false
    }
  }

  const changePassword = async (passwordData) => {
    try {
      loading.value = true
      await authAPI.changePassword(passwordData)
      toast.success('Пароль змінено!')
      return { success: true }
    } catch (error) {
      console.error('Change password error:', error)
      const message = error.response?.data?.detail || 
                     error.response?.data?.old_password?.[0] ||
                     error.response?.data?.new_password?.[0] ||
                     'Помилка зміни пароля'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      loading.value = false
    }
  }

  // Initialize auth on app load
  const init = async () => {
    const token = Cookies.get('access_token')
    if (token) {
      await fetchProfile()
    }
  }

  return {
    user,
    loading,
    isAuthenticated,
    isStaff,
    login,
    register,
    logout,
    fetchProfile,
    updateProfile,
    changePassword,
    init,
  }
})