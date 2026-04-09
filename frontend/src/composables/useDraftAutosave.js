import { watch, onUnmounted } from 'vue'

const AUTOSAVE_DELAY = 2000 // 2 секунди після останньої зміни

export function useDraftAutosave(key, formRef) {
  let timer = null

  // Завантажити збережений чернетку
  const loadDraft = () => {
    try {
      const saved = localStorage.getItem(key)
      return saved ? JSON.parse(saved) : null
    } catch {
      return null
    }
  }

  // Зберегти чернетку
  const saveDraft = (data) => {
    try {
      localStorage.setItem(key, JSON.stringify({
        ...data,
        savedAt: new Date().toISOString(),
      }))
    } catch (e) {
      console.warn('Не вдалося зберегти чернетку:', e)
    }
  }

  // Видалити чернетку (після успішного збереження на сервері)
  const clearDraft = () => {
    localStorage.removeItem(key)
  }

  // Запустити автосейв при зміні форми
  const startAutosave = () => {
    watch(
      formRef,
      (val) => {
        clearTimeout(timer)
        timer = setTimeout(() => saveDraft(val), AUTOSAVE_DELAY)
      },
      { deep: true }
    )
  }

  onUnmounted(() => clearTimeout(timer))

  return { loadDraft, saveDraft, clearDraft, startAutosave }
}