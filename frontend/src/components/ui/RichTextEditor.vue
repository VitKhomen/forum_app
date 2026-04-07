<template>
  <div class="rich-editor border border-gray-300 dark:border-gray-600 rounded-lg overflow-hidden">

    <!-- Тулбар -->
    <div
      v-if="editor"
      class="flex flex-wrap gap-1 p-2 bg-gray-50 dark:bg-gray-700 border-b border-gray-300 dark:border-gray-600"
    >
      <!-- Форматування тексту -->
      <div class="flex gap-1 pr-2 border-r border-gray-300 dark:border-gray-500">
        <button type="button" title="Жирний (Ctrl+B)" @click="editor.chain().focus().toggleBold().run()"
          :class="btnClass(editor.isActive('bold'))">
          <strong>B</strong>
        </button>
        <button type="button" title="Курсив (Ctrl+I)" @click="editor.chain().focus().toggleItalic().run()"
          :class="btnClass(editor.isActive('italic'))">
          <em>I</em>
        </button>
        <button type="button" title="Підкреслений (Ctrl+U)" @click="editor.chain().focus().toggleUnderline().run()"
          :class="btnClass(editor.isActive('underline'))">
          <span style="text-decoration: underline;">U</span>
        </button>
        <button type="button" title="Виділення" @click="editor.chain().focus().toggleHighlight().run()"
          :class="btnClass(editor.isActive('highlight'))">
          🖊
        </button>
      </div>

      <!-- Заголовки -->
      <div class="flex gap-1 pr-2 border-r border-gray-300 dark:border-gray-500">
        <button
          v-for="level in [1, 2, 3]"
          :key="level"
          type="button"
          :title="`Заголовок ${level}`"
          @click="editor.chain().focus().toggleHeading({ level }).run()"
          :class="btnClass(editor.isActive('heading', { level }))"
        >
          H{{ level }}
        </button>
      </div>

      <!-- Списки -->
      <div class="flex gap-1 pr-2 border-r border-gray-300 dark:border-gray-500">
        <button type="button" title="Маркований список" @click="editor.chain().focus().toggleBulletList().run()"
          :class="btnClass(editor.isActive('bulletList'))">
          ≡
        </button>
        <button type="button" title="Нумерований список" @click="editor.chain().focus().toggleOrderedList().run()"
          :class="btnClass(editor.isActive('orderedList'))">
          1.
        </button>
      </div>

      <!-- Блоки -->
      <div class="flex gap-1 pr-2 border-r border-gray-300 dark:border-gray-500">
        <button type="button" title="Цитата" @click="editor.chain().focus().toggleBlockquote().run()"
          :class="btnClass(editor.isActive('blockquote'))">
          ❝
        </button>
        <button type="button" title="Блок коду" @click="editor.chain().focus().toggleCodeBlock().run()"
          :class="btnClass(editor.isActive('codeBlock'))">
          &lt;/&gt;
        </button>
        <button type="button" title="Горизонтальна лінія" @click="editor.chain().focus().setHorizontalRule().run()"
          :class="btnClass(false)">
          —
        </button>
      </div>

      <!-- Вирівнювання -->
      <div class="flex gap-1 pr-2 border-r border-gray-300 dark:border-gray-500">
        <button
          v-for="align in alignments"
          :key="align.value"
          type="button"
          :title="align.title"
          @click="editor.chain().focus().setTextAlign(align.value).run()"
          :class="btnClass(editor.isActive({ textAlign: align.value }))"
        >
          {{ align.icon }}
        </button>
      </div>

      <!-- Посилання -->
      <div class="flex gap-1 pr-2 border-r border-gray-300 dark:border-gray-500">
        <button type="button" title="Посилання" @click="setLink" :class="btnClass(editor.isActive('link'))">
          🔗
        </button>
        <button
          v-if="editor.isActive('link')"
          type="button"
          title="Прибрати посилання"
          @click="editor.chain().focus().unsetLink().run()"
          :class="btnClass(false)"
        >
          🚫
        </button>
      </div>

      <!-- Undo / Redo -->
      <div class="flex gap-1 ml-auto">
        <button
          type="button"
          title="Відмінити (Ctrl+Z)"
          :disabled="!editor.can().undo()"
          @click="editor.chain().focus().undo().run()"
          :class="btnClass(false)"
          class="disabled:opacity-40 disabled:cursor-not-allowed"
        >
          ↩
        </button>
        <button
          type="button"
          title="Повторити (Ctrl+Y)"
          :disabled="!editor.can().redo()"
          @click="editor.chain().focus().redo().run()"
          :class="btnClass(false)"
          class="disabled:opacity-40 disabled:cursor-not-allowed"
        >
          ↪
        </button>
      </div>
    </div>

    <!-- Область редагування -->
    <EditorContent :editor="editor" class="tiptap-wrapper" />

    <!-- Лічильник символів -->
    <div
      v-if="editor"
      class="flex justify-end px-3 py-1 text-xs text-gray-400 dark:text-gray-500
             border-t border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700"
    >
      {{ charCount }} символів
    </div>
  </div>
</template>

<script setup>
import { computed, watch, onBeforeUnmount } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import Underline from '@tiptap/extension-underline'
import Link from '@tiptap/extension-link'
import Placeholder from '@tiptap/extension-placeholder'
import TextAlign from '@tiptap/extension-text-align'
import Highlight from '@tiptap/extension-highlight'

const props = defineProps({
  modelValue:  { type: String, default: '' },
  placeholder: { type: String, default: 'Напишіть текст посту...' },
})

const emit = defineEmits(['update:modelValue'])

// Класи кнопок тулбара — звичайна функція замість окремого компонента
const btnClass = (active) => [
  'px-2 py-1 rounded text-sm font-medium transition-colors min-w-[28px]',
  active
    ? 'bg-blue-600 text-white'
    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600',
]

const alignments = [
  { value: 'left',   icon: '⬅', title: 'По лівому краю' },
  { value: 'center', icon: '↔', title: 'По центру'       },
  { value: 'right',  icon: '➡', title: 'По правому краю' },
]

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit,
    Underline,
    Highlight,
    TextAlign.configure({ types: ['heading', 'paragraph'] }),
    Link.configure({
      openOnClick: false,
      HTMLAttributes: {
        target: '_blank',
        rel:    'noopener noreferrer',
      },
    }),
    Placeholder.configure({
      placeholder: props.placeholder,
    }),
  ],
  onUpdate({ editor }) {
    const html = editor.isEmpty ? '' : editor.getHTML()
    emit('update:modelValue', html)
  },
})

// Кількість символів через computed щоб не викликати storage напряму в template
const charCount = computed(() => {
  if (!editor.value) return 0
  return editor.value.getText().length
})

// Синхронізація при зміні ззовні (reset форми тощо)
watch(() => props.modelValue, (val) => {
  if (!editor.value) return
  const current = editor.value.isEmpty ? '' : editor.value.getHTML()
  if (val !== current) {
    editor.value.commands.setContent(val || '', false)
  }
})

const setLink = () => {
  if (!editor.value) return
  const prev = editor.value.getAttributes('link').href || ''
  const url  = window.prompt('Введіть URL посилання:', prev)
  if (url === null) return
  if (url === '') {
    editor.value.chain().focus().unsetLink().run()
    return
  }
  editor.value.chain().focus().setLink({ href: url }).run()
}

onBeforeUnmount(() => editor.value?.destroy())
</script>

<style scoped>
/* Область редагування */
.tiptap-wrapper :deep(.tiptap) {
  outline: none;
  min-height: 200px;
  padding: 1rem;
  background: white;
  color: #111827;
}

/* Dark mode */
:global(.dark) .tiptap-wrapper :deep(.tiptap) {
  background: #1f2937;
  color: white;
}

/* Placeholder */
.tiptap-wrapper :deep(.tiptap p.is-editor-empty:first-child::before) {
  content: attr(data-placeholder);
  color: #9ca3af;
  float: left;
  height: 0;
  pointer-events: none;
}

/* Заголовки */
.tiptap-wrapper :deep(.tiptap h1) {
  font-size: 1.875rem;
  font-weight: 700;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
}
.tiptap-wrapper :deep(.tiptap h2) {
  font-size: 1.5rem;
  font-weight: 700;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
}
.tiptap-wrapper :deep(.tiptap h3) {
  font-size: 1.25rem;
  font-weight: 700;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

/* Параграф */
.tiptap-wrapper :deep(.tiptap p) {
  margin-bottom: 0.75rem;
  line-height: 1.75;
}

/* Списки */
.tiptap-wrapper :deep(.tiptap ul) {
  list-style-type: disc;
  padding-left: 1.5rem;
  margin-bottom: 0.75rem;
}
.tiptap-wrapper :deep(.tiptap ol) {
  list-style-type: decimal;
  padding-left: 1.5rem;
  margin-bottom: 0.75rem;
}
.tiptap-wrapper :deep(.tiptap li) {
  margin-bottom: 0.25rem;
}

/* Цитата */
.tiptap-wrapper :deep(.tiptap blockquote) {
  border-left: 4px solid #60a5fa;
  padding-left: 1rem;
  font-style: italic;
  color: #6b7280;
  margin: 1rem 0;
}
:global(.dark) .tiptap-wrapper :deep(.tiptap blockquote) {
  color: #9ca3af;
}

/* Інлайн код */
.tiptap-wrapper :deep(.tiptap code) {
  background: #f3f4f6;
  color: #dc2626;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-family: monospace;
}
:global(.dark) .tiptap-wrapper :deep(.tiptap code) {
  background: #374151;
  color: #f87171;
}

/* Блок коду */
.tiptap-wrapper :deep(.tiptap pre) {
  background: #111827;
  color: #f3f4f6;
  border-radius: 0.5rem;
  padding: 1rem;
  margin: 1rem 0;
  overflow-x: auto;
}
.tiptap-wrapper :deep(.tiptap pre code) {
  background: transparent;
  color: inherit;
  padding: 0;
}

/* Горизонтальна лінія */
.tiptap-wrapper :deep(.tiptap hr) {
  border-color: #d1d5db;
  margin: 1.5rem 0;
}
:global(.dark) .tiptap-wrapper :deep(.tiptap hr) {
  border-color: #4b5563;
}

/* Виділення */
.tiptap-wrapper :deep(.tiptap mark) {
  background: #fef08a;
  border-radius: 0.125rem;
  padding: 0 0.125rem;
}
:global(.dark) .tiptap-wrapper :deep(.tiptap mark) {
  background: #713f12;
}

/* Посилання */
.tiptap-wrapper :deep(.tiptap a) {
  color: #2563eb;
  text-decoration: underline;
}
:global(.dark) .tiptap-wrapper :deep(.tiptap a) {
  color: #60a5fa;
}
</style>