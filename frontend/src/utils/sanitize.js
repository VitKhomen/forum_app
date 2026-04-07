import DOMPurify from 'dompurify'

export const sanitize = (html) =>
  DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3',
      'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
      'a', 'hr', 'mark', 'span',
    ],
    ALLOWED_ATTR: ['href', 'target', 'rel', 'class', 'style'],
  })