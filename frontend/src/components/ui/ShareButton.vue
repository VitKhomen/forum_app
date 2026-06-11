<template>
  <div class="relative" ref="wrapperRef">
    <button
      @click="toggleDropdown"
      class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium
             border border-gray-200 dark:border-gray-700
             text-gray-600 dark:text-gray-400
             hover:bg-gray-50 dark:hover:bg-gray-800
             hover:text-gray-900 dark:hover:text-white
             transition-all"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0
             1 1 0-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 1 0 5.367-2.684
             3 3 0 0 0-5.367 2.684zm0 9.316a3 3 0 1 0 5.368 2.684 3 3 0 0 0-5.368-2.684z"
        />
      </svg>
      <span class="hidden sm:inline">Поділитись</span>
    </button>

    <Transition name="dropdown-pop">
      <div
        v-if="open"
        class="absolute right-0 top-full mt-2 z-50
               bg-white dark:bg-gray-900
               border border-gray-200 dark:border-gray-700
               rounded-xl shadow-xl overflow-hidden
               min-w-[210px]"
      >
        <!-- Copy Link -->
        <button
          @click="copyLink"
          class="w-full flex items-center gap-3 px-4 py-3 text-sm text-left
                 text-gray-700 dark:text-gray-300
                 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          <Transition name="icon-swap" mode="out-in">
            <svg v-if="!copied" key="copy" class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
              />
            </svg>
            <svg v-else key="check" class="w-4 h-4 flex-shrink-0 text-green-500" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
          </Transition>
          <span>{{ copied ? 'Скопійовано!' : 'Копіювати посилання' }}</span>
        </button>

        <div class="h-px bg-gray-100 dark:bg-gray-800" />

        <!-- Telegram -->
        <button
          @click="shareToTelegram"
          class="w-full flex items-center gap-3 px-4 py-3 text-sm text-left
                 text-gray-700 dark:text-gray-300
                 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
        >
          <svg class="w-4 h-4 flex-shrink-0 text-[#2AABEE]" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97
              9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.447 1.394c-.16.16-.295.295-.605.295l.213-3.053
              5.56-5.023c.242-.213-.054-.333-.373-.12L7.412 14.587l-2.95-.924c-.64-.203-.654-.64.135-.954
              l11.57-4.461c.537-.194 1.006.131.727.973z"/>
          </svg>
          Telegram
        </button>

        <!-- Twitter / X -->
        <button
          @click="shareToTwitter"
          class="w-full flex items-center gap-3 px-4 py-3 text-sm text-left
                 text-gray-700 dark:text-gray-300
                 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          <svg class="w-4 h-4 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.23H2.748
              l7.73-8.835L1.254 2.25H8.08l4.253 5.622 5.91-5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
          </svg>
          Twitter / X
        </button>

        <!-- Native Share (якщо підтримується) -->
        <template v-if="hasNativeShare">
          <div class="h-px bg-gray-100 dark:bg-gray-800" />
          <button
            @click="nativeShare"
            class="w-full flex items-center gap-3 px-4 py-3 text-sm text-left
                   text-gray-700 dark:text-gray-300
                   hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round"
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
            </svg>
            Інші способи
          </button>
        </template>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  // URL для шерингу (якщо не передано — береться поточний URL)
  url:   { type: String, default: '' },
  // Заголовок поста
  title: { type: String, default: '' },
  // Короткий опис для native share
  text:  { type: String, default: '' },
})

const open       = ref(false)
const copied     = ref(false)
const wrapperRef = ref(null)

const shareUrl = computed(() => props.url || (typeof window !== 'undefined' ? window.location.href : ''))

const hasNativeShare = typeof navigator !== 'undefined' && !!navigator.share

const toggleDropdown = () => { open.value = !open.value }

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
  } catch {
    // Fallback для старих браузерів
    const el = document.createElement('textarea')
    el.value = shareUrl.value
    el.style.position = 'fixed'
    el.style.opacity  = '0'
    document.body.appendChild(el)
    el.select()
    document.execCommand('copy')
    document.body.removeChild(el)
  }
  copied.value = true
  setTimeout(() => {
    copied.value = false
    open.value   = false
  }, 1800)
}

const shareToTelegram = () => {
  const url = `https://t.me/share/url?url=${encodeURIComponent(shareUrl.value)}&text=${encodeURIComponent(props.title)}`
  window.open(url, '_blank', 'noopener,noreferrer,width=600,height=500')
  open.value = false
}

const shareToTwitter = () => {
  const text = props.title ? `${props.title} — ${shareUrl.value}` : shareUrl.value
  const url  = `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}`
  window.open(url, '_blank', 'noopener,noreferrer,width=600,height=400')
  open.value = false
}

const nativeShare = async () => {
  try {
    await navigator.share({
      title: props.title,
      text:  props.text || props.title,
      url:   shareUrl.value,
    })
  } catch (e) {
    if (e.name !== 'AbortError') console.error(e)
  }
  open.value = false
}

const handleOutside = (e) => {
  if (wrapperRef.value && !wrapperRef.value.contains(e.target)) open.value = false
}

onMounted(()  => document.addEventListener('click', handleOutside))
onUnmounted(() => document.removeEventListener('click', handleOutside))
</script>

<style scoped>
.dropdown-pop-enter-active { transition: all 0.15s cubic-bezier(0.34, 1.56, 0.64, 1); }
.dropdown-pop-leave-active { transition: all 0.1s ease; }
.dropdown-pop-enter-from  { opacity: 0; transform: scale(0.92) translateY(-6px); }
.dropdown-pop-leave-to    { opacity: 0; transform: scale(0.96) translateY(-4px); }

.icon-swap-enter-active, .icon-swap-leave-active { transition: all 0.15s ease; }
.icon-swap-enter-from { opacity: 0; transform: scale(0.5); }
.icon-swap-leave-to   { opacity: 0; transform: scale(1.3); }
</style>