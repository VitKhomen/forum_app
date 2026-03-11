<template>
  <Teleport to="body">
    <Transition name="picker-pop">
      <div
        v-if="modelValue"
        ref="pickerRef"
        class="emoji-picker"
        :style="pickerStyle"
        @mousedown.prevent.stop
        @wheel.prevent="onWheel"
      >
        <!-- Пошук -->
        <div class="picker-search">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            ref="searchInput"
            v-model="searchQuery"
            placeholder="Пошук..."
            class="search-input"
            @keydown.esc.stop="$emit('update:modelValue', false)"
          />
          <button v-if="searchQuery" @mousedown.prevent="searchQuery = ''" class="clear-btn">✕</button>
        </div>

        <!-- Нещодавні (фіксований блок) -->
        <div v-if="!searchQuery && recentEmojis.length" class="recent-bar">
          <span class="recent-label">Нещодавні</span>
          <div class="recent-grid">
            <button
              v-for="emoji in recentEmojis"
              :key="'r-' + emoji.emoji"
              @mousedown.prevent="selectEmoji(emoji.emoji)"
              @mouseenter="hoveredEmoji = emoji.emoji; hoveredLabel = emoji.label"
              @mouseleave="hoveredEmoji = ''; hoveredLabel = ''"
              class="emoji-btn"
              :title="emoji.label"
            >{{ emoji.emoji }}</button>
          </div>
        </div>

        <!-- Решта емодзі (скролиться) -->
        <div class="emoji-grid-wrapper" ref="gridWrapper">
          <p v-if="searchQuery && !visibleEmojis.length" class="no-results">Нічого не знайдено</p>
          <div v-else class="emoji-grid">
            <button
              v-for="emoji in visibleEmojis"
              :key="emoji.emoji"
              @mousedown.prevent="selectEmoji(emoji.emoji)"
              @mouseenter="hoveredEmoji = emoji.emoji; hoveredLabel = emoji.label"
              @mouseleave="hoveredEmoji = ''; hoveredLabel = ''"
              class="emoji-btn"
              :title="emoji.label"
            >{{ emoji.emoji }}</button>
          </div>
        </div>

        <!-- Футер -->
        <div class="picker-footer">
          <span class="preview-emoji">{{ hoveredEmoji || '😊' }}</span>
          <span class="preview-label">{{ hoveredLabel || 'Оберіть емодзі' }}</span>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  anchorEl:   { type: Object, default: null },
})
const emit = defineEmits(['update:modelValue', 'select'])

const pickerRef   = ref(null)
const searchInput = ref(null)
const gridWrapper = ref(null)
const searchQuery = ref('')
const hoveredEmoji = ref('')
const hoveredLabel = ref('')
const pickerStyle = ref({})

// ── Всі емодзі одним списком ───────────────────────────────────
const ALL_EMOJIS = [
  // Нещодавні додаються динамічно

  // Смайлики
  { emoji: '😀', label: 'Усміхнений' }, { emoji: '😃', label: 'Радісний' },
  { emoji: '😄', label: 'Веселий' }, { emoji: '😁', label: 'Зубастий' },
  { emoji: '😆', label: 'Сміється' }, { emoji: '😅', label: 'Ой-ой' },
  { emoji: '🤣', label: 'Качається від сміху' }, { emoji: '😂', label: 'Сльози від сміху' },
  { emoji: '🙂', label: 'Злегка усміхнений' }, { emoji: '🙃', label: 'Догори ногами' },
  { emoji: '😉', label: 'Підморгує' }, { emoji: '😊', label: 'Ніяковий' },
  { emoji: '😇', label: 'Ангел' }, { emoji: '🥰', label: 'Закоханий' },
  { emoji: '😍', label: 'Очі-серця' }, { emoji: '🤩', label: 'Зірки в очах' },
  { emoji: '😘', label: 'Повітряний поцілунок' }, { emoji: '😗', label: 'Цмок' },
  { emoji: '🥲', label: 'Усміхнена сльоза' }, { emoji: '😋', label: 'Смачно' },
  { emoji: '😛', label: 'Язик' }, { emoji: '😜', label: 'Підморгує з язиком' },
  { emoji: '🤪', label: 'Шалений' }, { emoji: '😝', label: 'Язик з закритими очима' },
  { emoji: '🤑', label: 'Гроші в очах' }, { emoji: '🤗', label: 'Обіймає' },
  { emoji: '🤭', label: 'Прикрив рота' }, { emoji: '🤫', label: 'Тихо' },
  { emoji: '🤔', label: 'Думає' }, { emoji: '🤐', label: 'Замовк' },
  { emoji: '🤨', label: 'Підіймає брову' }, { emoji: '😐', label: 'Нейтральний' },
  { emoji: '😑', label: 'Без виразу' }, { emoji: '😶', label: 'Без рота' },
  { emoji: '😏', label: 'Ухмилка' }, { emoji: '😒', label: 'Незадоволений' },
  { emoji: '🙄', label: 'Очі вгору' }, { emoji: '😬', label: 'Гримаса' },
  { emoji: '🤥', label: 'Брехун' }, { emoji: '😌', label: 'Розслаблений' },
  { emoji: '😔', label: 'Задумливий' }, { emoji: '😪', label: 'Сонний' },
  { emoji: '🤤', label: 'Слинить' }, { emoji: '😴', label: 'Спить' },
  { emoji: '😷', label: 'Маска' }, { emoji: '🤒', label: 'Хворий' },
  { emoji: '🤕', label: 'Травма' }, { emoji: '🤢', label: 'Нудить' },
  { emoji: '🤮', label: 'Блювота' }, { emoji: '🤧', label: 'Чхає' },
  { emoji: '🥵', label: 'Жарко' }, { emoji: '🥶', label: 'Холодно' },
  { emoji: '🥴', label: 'Запаморочення' }, { emoji: '😵', label: 'Приголомшений' },
  { emoji: '🤯', label: 'Вибух мозку' }, { emoji: '🤠', label: 'Ковбой' },
  { emoji: '🥳', label: 'Святкує' }, { emoji: '🥸', label: 'Маскується' },
  { emoji: '😎', label: 'Крутий' }, { emoji: '🤓', label: 'Ботанік' },
  { emoji: '🧐', label: 'З монокль' }, { emoji: '😕', label: 'Збентежений' },
  { emoji: '😟', label: 'Занепокоєний' }, { emoji: '🙁', label: 'Злегка сумний' },
  { emoji: '😮', label: 'Відкритий рот' }, { emoji: '😯', label: 'Здивований' },
  { emoji: '😲', label: 'Шокований' }, { emoji: '😳', label: 'Ніяковіє' },
  { emoji: '🥺', label: 'Благальні очі' }, { emoji: '😦', label: 'Стурбований' },
  { emoji: '😧', label: 'Мученицький' }, { emoji: '😨', label: 'Наляканий' },
  { emoji: '😰', label: 'Тривожний піт' }, { emoji: '😥', label: 'Засмучений' },
  { emoji: '😢', label: 'Плаче' }, { emoji: '😭', label: 'Ридає' },
  { emoji: '😱', label: 'Кричить від страху' }, { emoji: '😖', label: 'Збентежений' },
  { emoji: '😣', label: 'Намагається' }, { emoji: '😞', label: 'Розчарований' },
  { emoji: '😓', label: 'Піт' }, { emoji: '😩', label: 'Знесилений' },
  { emoji: '😫', label: 'Виснажений' }, { emoji: '🥱', label: 'Позіхає' },
  { emoji: '😤', label: 'Сопе' }, { emoji: '😡', label: 'Злий' },
  { emoji: '😠', label: 'Сердитий' }, { emoji: '🤬', label: 'Лається' },
  { emoji: '😈', label: 'Злий янгол' }, { emoji: '👿', label: 'Диявол' },
  { emoji: '💀', label: 'Череп' }, { emoji: '☠️', label: 'Череп і кістки' },
  { emoji: '💩', label: 'Какашка' }, { emoji: '🤡', label: 'Клоун' },
  { emoji: '👹', label: 'Демон' }, { emoji: '👺', label: 'Гоблін' },
  { emoji: '👻', label: 'Привид' }, { emoji: '👽', label: 'Прибулець' },
  { emoji: '👾', label: 'Монстр' }, { emoji: '🤖', label: 'Робот' },
  // Жести
  { emoji: '👋', label: 'Помахати' }, { emoji: '🤚', label: 'Долоня' },
  { emoji: '✋', label: 'Стоп' }, { emoji: '👌', label: 'ОК' },
  { emoji: '✌️', label: 'Перемога' }, { emoji: '🤞', label: 'Схрещені пальці' },
  { emoji: '🤟', label: 'Люблю' }, { emoji: '🤘', label: 'Рок' },
  { emoji: '🤙', label: 'Подзвони' }, { emoji: '👈', label: 'Вліво' },
  { emoji: '👉', label: 'Вправо' }, { emoji: '👆', label: 'Вгору' },
  { emoji: '👇', label: 'Вниз' }, { emoji: '👍', label: 'Лайк' },
  { emoji: '👎', label: 'Дизлайк' }, { emoji: '✊', label: 'Кулак' },
  { emoji: '👊', label: 'Удар' }, { emoji: '👏', label: 'Оплески' },
  { emoji: '🙌', label: 'Руки вгору' }, { emoji: '🤝', label: 'Рукостискання' },
  { emoji: '🙏', label: 'Молитва' }, { emoji: '💪', label: 'Біцепс' },
  { emoji: '✍️', label: 'Пише' },
  // Серця
  { emoji: '❤️', label: 'Червоне серце' }, { emoji: '🧡', label: 'Оранжеве серце' },
  { emoji: '💛', label: 'Жовте серце' }, { emoji: '💚', label: 'Зелене серце' },
  { emoji: '💙', label: 'Синє серце' }, { emoji: '💜', label: 'Фіолетове серце' },
  { emoji: '🖤', label: 'Чорне серце' }, { emoji: '🤍', label: 'Біле серце' },
  { emoji: '🤎', label: 'Коричневе серце' }, { emoji: '💔', label: 'Розбите серце' },
  { emoji: '💕', label: 'Два серця' }, { emoji: '💞', label: 'Кружляючі серця' },
  { emoji: '💓', label: 'Серце б\'ється' }, { emoji: '💗', label: 'Рожеве серце' },
  { emoji: '💖', label: 'Іскряче серце' }, { emoji: '💘', label: 'Серце зі стрілою' },
  { emoji: '💝', label: 'Серце з бантом' }, { emoji: '✨', label: 'Іскри' },
  { emoji: '⭐', label: 'Зірка' }, { emoji: '🌟', label: 'Сяюча зірка' },
  { emoji: '💫', label: 'Запаморочення' }, { emoji: '🔥', label: 'Вогонь' },
  { emoji: '💥', label: 'Вибух' }, { emoji: '💢', label: 'Злість' },
  { emoji: '💬', label: 'Бульбашка' }, { emoji: '💭', label: 'Думка' },
  { emoji: '💤', label: 'Сон' },
  // Природа
  { emoji: '🐶', label: 'Собака' }, { emoji: '🐱', label: 'Кіт' },
  { emoji: '🐰', label: 'Кролик' }, { emoji: '🦊', label: 'Лиса' },
  { emoji: '🐻', label: 'Ведмідь' }, { emoji: '🐼', label: 'Панда' },
  { emoji: '🐨', label: 'Коала' }, { emoji: '🐯', label: 'Тигр' },
  { emoji: '🦁', label: 'Лев' }, { emoji: '🐮', label: 'Корова' },
  { emoji: '🐷', label: 'Свиня' }, { emoji: '🐸', label: 'Жаба' },
  { emoji: '🐵', label: 'Мавпа' }, { emoji: '🐔', label: 'Курка' },
  { emoji: '🐧', label: 'Пінгвін' }, { emoji: '🦆', label: 'Качка' },
  { emoji: '🦅', label: 'Орел' }, { emoji: '🦉', label: 'Сова' },
  { emoji: '🦇', label: 'Кажан' }, { emoji: '🐺', label: 'Вовк' },
  { emoji: '🦄', label: 'Єдиноріг' }, { emoji: '🐝', label: 'Бджола' },
  { emoji: '🦋', label: 'Метелик' }, { emoji: '🌸', label: 'Цвітіння' },
  { emoji: '🌺', label: 'Гібіскус' }, { emoji: '🌻', label: 'Соняшник' },
  { emoji: '🌹', label: 'Троянда' }, { emoji: '🌷', label: 'Тюльпан' },
  { emoji: '🌿', label: 'Трава' }, { emoji: '🍀', label: 'Конюшина' },
  { emoji: '🍁', label: 'Кленовий лист' }, { emoji: '🌊', label: 'Хвиля' },
  { emoji: '☀️', label: 'Сонце' }, { emoji: '🌙', label: 'Місяць' },
  { emoji: '❄️', label: 'Сніжинка' }, { emoji: '🌈', label: 'Веселка' },
  // Їжа
  { emoji: '🍎', label: 'Яблуко' }, { emoji: '🍊', label: 'Мандарин' },
  { emoji: '🍋', label: 'Лимон' }, { emoji: '🍇', label: 'Виноград' },
  { emoji: '🍓', label: 'Полуниця' }, { emoji: '🍒', label: 'Вишня' },
  { emoji: '🍑', label: 'Персик' }, { emoji: '🥝', label: 'Ківі' },
  { emoji: '🍕', label: 'Піца' }, { emoji: '🍔', label: 'Гамбургер' },
  { emoji: '🌮', label: 'Тако' }, { emoji: '🍣', label: 'Суші' },
  { emoji: '🍜', label: 'Рамен' }, { emoji: '🍩', label: 'Пончик' },
  { emoji: '🎂', label: 'Торт' }, { emoji: '🍦', label: 'Морозиво' },
  { emoji: '☕', label: 'Кава' }, { emoji: '🧃', label: 'Сік' },
  { emoji: '🍺', label: 'Пиво' }, { emoji: '🍷', label: 'Вино' },
  { emoji: '🥂', label: 'Шампанське' }, { emoji: '🧁', label: 'Кекс' },
  { emoji: '🍿', label: 'Попкорн' }, { emoji: '🥪', label: 'Сендвіч' },
  // Активності та символи
  { emoji: '⚽', label: 'Футбол' }, { emoji: '🏀', label: 'Баскетбол' },
  { emoji: '🎾', label: 'Теніс' }, { emoji: '🎯', label: 'Ціль' },
  { emoji: '🎮', label: 'Відеоігри' }, { emoji: '🎲', label: 'Кубик' },
  { emoji: '🎨', label: 'Малювання' }, { emoji: '🎤', label: 'Мікрофон' },
  { emoji: '🎧', label: 'Навушники' }, { emoji: '🎸', label: 'Гітара' },
  { emoji: '🏆', label: 'Трофей' }, { emoji: '🥇', label: 'Золото' },
  { emoji: '✈️', label: 'Літак' }, { emoji: '🚀', label: 'Ракета' },
  { emoji: '🚗', label: 'Машина' }, { emoji: '🏠', label: 'Будинок' },
  { emoji: '🌍', label: 'Земля' }, { emoji: '🗺️', label: 'Карта' },
  { emoji: '🏔️', label: 'Гора' }, { emoji: '🏖️', label: 'Пляж' },
  { emoji: '🎉', label: 'Конфеті' }, { emoji: '🎊', label: 'Хлопавка' },
  { emoji: '🎁', label: 'Подарунок' }, { emoji: '💎', label: 'Діамант' },
  { emoji: '💯', label: '100' }, { emoji: '✅', label: 'Галочка' },
  { emoji: '❌', label: 'Хрест' }, { emoji: '❓', label: 'Питання' },
  { emoji: '❗', label: 'Оклик' }, { emoji: '⚡', label: 'Блискавка' },
  { emoji: '💡', label: 'Лампочка' }, { emoji: '🔔', label: 'Дзвінок' },
  { emoji: '🎵', label: 'Нота' }, { emoji: '🎶', label: 'Ноти' },
  { emoji: '🔴', label: 'Червоний' }, { emoji: '🟠', label: 'Оранжевий' },
  { emoji: '🟡', label: 'Жовтий' }, { emoji: '🟢', label: 'Зелений' },
  { emoji: '🔵', label: 'Синій' }, { emoji: '🟣', label: 'Фіолетовий' },
]

const RECENT_KEY = 'emoji_recent'
const MAX_RECENT = 16

const recentEmojis = ref(
  JSON.parse(localStorage.getItem(RECENT_KEY) || '[]').map(e => ({ emoji: e, label: 'Нещодавні' }))
)

const visibleEmojis = computed(() => {
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    return ALL_EMOJIS.filter(e =>
      e.label.toLowerCase().includes(q) || e.emoji.includes(q)
    ).slice(0, 80)
  }
  // Нещодавні показуються окремо вгорі — тут тільки решта
  const recentSet = new Set(recentEmojis.value.map(e => e.emoji))
  return ALL_EMOJIS.filter(e => !recentSet.has(e.emoji))
})

// ── Скрол колесом ─────────────────────────────────────────────
const onWheel = (e) => {
  const wrapper = gridWrapper.value
  if (!wrapper) return
  wrapper.scrollTop += e.deltaY
}

// ── Позиціонування ────────────────────────────────────────────
const updatePosition = () => {
  if (!props.anchorEl) return
  const anchor = props.anchorEl.$el || props.anchorEl
  const rect = anchor.getBoundingClientRect()
  const pickerH = 480
  const pickerW = 360
  const margin = 8

  let top = rect.top - pickerH - margin
  let left = rect.left

  if (top < margin) top = rect.bottom + margin
  if (left + pickerW > window.innerWidth - margin) left = window.innerWidth - pickerW - margin
  if (left < margin) left = margin

  pickerStyle.value = {
    position: 'fixed',
    top: `${top}px`,
    left: `${left}px`,
    zIndex: 9999,
  }
}

// ── Вибір ─────────────────────────────────────────────────────
const selectEmoji = (emoji) => {
  const recent = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]')
  const updated = [emoji, ...recent.filter(e => e !== emoji)].slice(0, MAX_RECENT)
  localStorage.setItem(RECENT_KEY, JSON.stringify(updated))
  recentEmojis.value = updated.map(e => ({ emoji: e, label: 'Нещодавні' }))
  emit('select', emoji)
}

// ── Клік поза picker ──────────────────────────────────────────
const handleOutsideClick = (e) => {
  if (!pickerRef.value) return
  const anchor = props.anchorEl?.$el || props.anchorEl
  if (pickerRef.value.contains(e.target)) return
  if (anchor?.contains(e.target)) return
  emit('update:modelValue', false)
}

watch(() => props.modelValue, async (val) => {
  if (val) {
    searchQuery.value = ''
    await nextTick()
    updatePosition()
    searchInput.value?.focus()
    document.addEventListener('click', handleOutsideClick)
  } else {
    document.removeEventListener('click', handleOutsideClick)
  }
})

onUnmounted(() => document.removeEventListener('click', handleOutsideClick))
</script>

<style scoped>
.emoji-picker {
  width: 360px;
  background: var(--picker-bg, #ffffff);
  border: 1px solid var(--picker-border, #e5e7eb);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,.18), 0 4px 16px rgba(0,0,0,.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  user-select: none;
}

:root.dark .emoji-picker, .dark .emoji-picker {
  --picker-bg: #1f2937;
  --picker-border: #374151;
  --search-text: #f3f4f6;
  --search-placeholder: #6b7280;
  --grid-hover: #374151;
  --label-color: #6b7280;
  --footer-bg: #111827;
  --footer-border: #374151;
  --footer-text: #9ca3af;
}

/* Пошук */
.picker-search {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--picker-border, #f3f4f6);
  flex-shrink: 0;
}
.search-icon { width: 14px; height: 14px; color: var(--search-placeholder, #9ca3af); flex-shrink: 0; }
.search-input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 13px;
  color: var(--search-text, #111827);
}
.search-input::placeholder { color: var(--search-placeholder, #9ca3af); }
.clear-btn {
  font-size: 11px;
  color: var(--search-placeholder, #9ca3af);
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  transition: color .15s;
}
.clear-btn:hover { color: #ef4444; }

/* Нещодавні */
.recent-bar {
  padding: 6px 8px 4px;
  border-bottom: 1px solid var(--picker-border, #f3f4f6);
  flex-shrink: 0;
}
.recent-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: .05em;
  color: var(--label-color, #9ca3af);
  display: block;
  margin-bottom: 2px;
}
.recent-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 2px;
}

/* Грід */
.emoji-grid-wrapper {
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px;
  height: 420px;
  scrollbar-width: thin;
  scrollbar-color: #d1d5db transparent;
}
.emoji-grid-wrapper::-webkit-scrollbar { width: 4px; }
.emoji-grid-wrapper::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 4px; }

.emoji-grid {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 2px;
}
.emoji-btn {
  font-size: 22px;
  line-height: 1;
  padding: 5px;
  border-radius: 8px;
  cursor: pointer;
  transition: background .1s, transform .1s;
  text-align: center;
}
.emoji-btn:hover {
  background: var(--grid-hover, #f3f4f6);
  transform: scale(1.2);
}
.no-results {
  text-align: center;
  padding: 40px 0;
  color: var(--label-color, #9ca3af);
  font-size: 13px;
}

/* Футер */
.picker-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-top: 1px solid var(--footer-border, #f3f4f6);
  background: var(--footer-bg, #fafafa);
  flex-shrink: 0;
}
.preview-emoji { font-size: 20px; }
.preview-label { font-size: 12px; color: var(--footer-text, #6b7280); }

/* Анімація появи */
.picker-pop-enter-active { transition: all .2s cubic-bezier(0.34, 1.56, 0.64, 1); }
.picker-pop-leave-active { transition: all .12s ease; }
.picker-pop-enter-from   { opacity: 0; transform: scale(0.9) translateY(8px); }
.picker-pop-leave-to     { opacity: 0; transform: scale(0.95) translateY(4px); }
</style>