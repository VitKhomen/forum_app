// src/composables/useInfiniteScroll.js
import { ref, watchEffect, onUnmounted } from 'vue'

export function useInfiniteScroll(fetchFn) {
  const items       = ref([])
  const loading     = ref(false)
  const hasMore     = ref(true)
  const currentPage = ref(1)
  const triggerEl   = ref(null)
  const error       = ref(null)

  let observer = null

  const loadMore = async () => {
    if (loading.value || !hasMore.value) return
    loading.value = true
    error.value = null

    try {
      const { data } = await fetchFn({ page: currentPage.value })
      const newItems = data.results || []
      items.value.push(...newItems)

      hasMore.value = !!data.next
      if (hasMore.value) currentPage.value++
    } catch (e) {
      error.value = e
      console.error('useInfiniteScroll error:', e)
    } finally {
      loading.value = false
    }
  }

  const reset = async () => {
    items.value       = []
    currentPage.value = 1
    hasMore.value     = true
    error.value       = null
    await loadMore() // одразу завантажуємо першу сторінку після ресету
  }

  // watchEffect стежить за triggerEl — запускається як тільки елемент з'явився в DOM
  const stopWatch = watchEffect(() => {
    if (!triggerEl.value) return

    observer?.disconnect()
    observer = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) loadMore() },
      { rootMargin: '200px' }
    )
    observer.observe(triggerEl.value)
  })

  onUnmounted(() => {
    observer?.disconnect()
    stopWatch()
  })

  return { items, loading, hasMore, error, triggerEl, loadMore, reset }
}