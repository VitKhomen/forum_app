import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const currentTheme = ref('light')

  const applyTheme = (theme) => {
    console.log('🎨 Applying theme:', theme) // ✅ DEBUG
    
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
      console.log('✅ Added dark class')
    } else {
      document.documentElement.classList.remove('dark')
      console.log('✅ Removed dark class')
    }
  }

  const toggleTheme = () => {
    console.log('🔄 Toggle theme from:', currentTheme.value) // ✅ DEBUG
    currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light'
    console.log('🔄 Toggle theme to:', currentTheme.value) // ✅ DEBUG
  }

  const setTheme = (theme) => {
    console.log('📝 Set theme to:', theme) // ✅ DEBUG
    if (theme === 'light' || theme === 'dark') {
      currentTheme.value = theme
    }
  }

  // Ініціалізація
  const initTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    console.log('💾 Saved theme from localStorage:', savedTheme) // ✅ DEBUG
    
    if (savedTheme === 'dark' || savedTheme === 'light') {
      currentTheme.value = savedTheme
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      currentTheme.value = 'dark'
      console.log('🖥️ System prefers dark mode')
    } else {
      currentTheme.value = 'light'
    }
    
    applyTheme(currentTheme.value)
  }

  // Спостерігаємо за змінами
  watch(currentTheme, (newTheme) => {
    console.log('👀 Theme changed to:', newTheme) // ✅ DEBUG
    applyTheme(newTheme)
    localStorage.setItem('theme', newTheme)
  })

  return {
    currentTheme,
    toggleTheme,
    setTheme,
    initTheme,
  }
})