import { ref, watch, onMounted } from 'vue'

const THEME_KEY = 'theme-preference'

// Глобальний стан теми (синглтон)
const isDark = ref(false)

export function useTheme() {
  // Ініціалізація теми з localStorage або системних налаштувань
  const initTheme = () => {
    const stored = localStorage.getItem(THEME_KEY)
    
    if (stored) {
      // Якщо є збережене значення
      isDark.value = stored === 'dark'
    } else {
      // Якщо немає, перевіряємо системні налаштування
      isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
    }
    
    applyTheme()
  }

  // Застосування теми до документа
  const applyTheme = () => {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // Перемикання теми
  const toggleTheme = () => {
    isDark.value = !isDark.value
    localStorage.setItem(THEME_KEY, isDark.value ? 'dark' : 'light')
    applyTheme()
  }

  // Встановлення конкретної теми
  const setTheme = (theme) => {
    isDark.value = theme === 'dark'
    localStorage.setItem(THEME_KEY, theme)
    applyTheme()
  }

  // Відслідковуємо зміни isDark
  watch(isDark, () => {
    applyTheme()
  })

  // Ініціалізація при монтуванні
  onMounted(() => {
    initTheme()
  })

  return {
    isDark,
    toggleTheme,
    setTheme,
    initTheme
  }
}