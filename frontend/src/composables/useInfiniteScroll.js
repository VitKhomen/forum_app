import { ref, watchEffect, onUnmounted } from 'vue'

export function useInfiniteScroll(fetchFn) {
  const items       = ref([])
  const loading     = ref(false)
  const hasMore     = ref(true)
  const offset      = ref(0)
  const totalCount  = ref(0)
  const error       = ref(null)
  const triggerEl   = ref(null)

  let observer = null

  const loadMore = async () => {
    if (loading.value || !hasMore.value) return
    loading.value = true
    error.value   = null

    try {
      const { data } = await fetchFn({ offset: offset.value })
      const newItems = data.results || []

      items.value.push(...newItems)

      // Зберігаємо загальну кількість з першої сторінки
      if (offset.value === 0) {
        totalCount.value = data.count || 0
      }

      hasMore.value = !!data.next
      if (hasMore.value) offset.value += (data.results?.length || 0)
    } catch (e) {
      error.value = e
      console.error('useInfiniteScroll error:', e)
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    items.value       = []
    offset.value      = 0
    hasMore.value     = true
    totalCount.value  = 0
    error.value       = null
    loadMore()
  }

  // watchEffect реагує як тільки triggerEl з'являється в DOM
  const stopWatch = watchEffect(() => {
    if (!triggerEl.value) return

    observer?.disconnect()
    observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) loadMore()
      },
      { rootMargin: '200px' }
    )
    observer.observe(triggerEl.value)
  })

  onUnmounted(() => {
    observer?.disconnect()
    stopWatch()
  })

  return {
    items,
    loading,
    hasMore,
    error,
    totalCount,
    triggerEl,
    loadMore,
    reset,
  }
}