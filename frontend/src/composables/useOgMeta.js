import { onUnmounted } from 'vue'

// ── Допоміжні функції ────────────────────────────────────────────────────────

/** Встановити або створити <meta> тег у <head> */
const setMeta = (attrs) => {
  // Шукаємо за першим ключем (property або name)
  const key   = attrs.property ? 'property' : 'name'
  const value = attrs[key]
  let el = document.querySelector(`meta[${key}="${value}"]`)

  if (!el) {
    el = document.createElement('meta')
    document.head.appendChild(el)
  }
  Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v))
}

/** Видалити <meta> тег */
const removeMeta = (key, value) => {
  const el = document.querySelector(`meta[${key}="${value}"]`)
  if (el) el.remove()
}

/** Зберегти оригінальний <title> щоб відновити при unmount */
let originalTitle = ''

// ── OG-теги які ми виставляємо ───────────────────────────────────────────────

const OG_TAGS = [
  'og:title', 'og:description', 'og:image', 'og:url',
  'og:type',  'og:site_name',
  'twitter:card', 'twitter:title', 'twitter:description', 'twitter:image',
]

// ── Composable ───────────────────────────────────────────────────────────────

export function useOgMeta() {
  /**
   * Виставляє всі потрібні мета-теги для поста.
   *
   * @param {Object} post - об'єкт поста з PostDetailSerializer
   */
  const setPostMeta = (post) => {
    if (typeof document === 'undefined') return

    // Зберігаємо оригінальний title першого разу
    if (!originalTitle) originalTitle = document.title

    const siteUrl  = window.location.origin
    const postUrl  = `${siteUrl}/posts/${post.slug}`
    const siteName = 'JustForum'

    // Заголовок — обрізаємо до 70 символів (ліміт OG)
    const title = (post.title || '').slice(0, 70)

    // Опис — чистий текст без HTML, обрізаємо до 200 символів
    const rawDescription = (post.excerpt || post.content || '')
      .replace(/<[^>]*>/g, '')
      .trim()
    const description = rawDescription.slice(0, 200) + (rawDescription.length > 200 ? '…' : '')

    // Зображення — головне або перше з галереї
    const image = post.image
      || (post.images && post.images[0]?.image)
      || `${siteUrl}/og-default.png`   // ← замените на ваш fallback

    // <title>
    document.title = `${title} — ${siteName}`

    // Open Graph
    setMeta({ property: 'og:type',        content: 'article' })
    setMeta({ property: 'og:site_name',   content: siteName })
    setMeta({ property: 'og:url',         content: postUrl })
    setMeta({ property: 'og:title',       content: title })
    setMeta({ property: 'og:description', content: description })
    setMeta({ property: 'og:image',       content: image })
    // Явні розміри допомагають Telegram/VK підхопити картинку
    setMeta({ property: 'og:image:width',  content: '1200' })
    setMeta({ property: 'og:image:height', content: '630' })

    // Twitter Card (потрібна для Twitter/X preview)
    setMeta({ name: 'twitter:card',        content: 'summary_large_image' })
    setMeta({ name: 'twitter:title',       content: title })
    setMeta({ name: 'twitter:description', content: description })
    setMeta({ name: 'twitter:image',       content: image })

    // Canonical
    let canonical = document.querySelector('link[rel="canonical"]')
    if (!canonical) {
      canonical = document.createElement('link')
      canonical.rel = 'canonical'
      document.head.appendChild(canonical)
    }
    canonical.href = postUrl
  }

  /**
   * Видаляє виставлені мета-теги і відновлює оригінальний title.
   * Викликати в onUnmounted.
   */
  const clearMeta = () => {
    if (typeof document === 'undefined') return

    OG_TAGS.forEach((tag) => {
      const key = tag.startsWith('og:') ? 'property' : 'name'
      removeMeta(key, tag)
    })
    ;['og:image:width', 'og:image:height'].forEach(t => removeMeta('property', t))

    if (originalTitle) {
      document.title = originalTitle
      originalTitle  = ''
    }
  }

  // Автоматичне очищення при unmount компонента
  onUnmounted(clearMeta)

  return { setPostMeta, clearMeta }
}