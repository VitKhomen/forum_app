<template>
  <div class="relative w-full">
    <Swiper
      :modules="modules"
      :slides-per-view="1"
      :space-between="16"
      :loop="true"
      :autoplay="{
        delay: interval,
        disableOnInteraction: false,
      }"
      :navigation="{
        nextEl: '.swiper-button-next-custom',
        prevEl: '.swiper-button-prev-custom',
      }"
      :pagination="{
        clickable: true,
        el: '.swiper-pagination-custom',
      }"
      :breakpoints="{
        640: {
          slidesPerView: 2,
          spaceBetween: 16,
        },
        1024: {
          slidesPerView: 5,
          spaceBetween: 16,
        },
      }"
      class="!pb-12"
    >
      <SwiperSlide v-for="post in posts" :key="post.id">
        <article class="relative h-[400px] overflow-hidden rounded-lg shadow-xl hover:shadow-2xl transition-shadow duration-300">
          <!-- Image with overlay -->
          <img
            v-if="post.image"
            :src="post.image"
            :alt="post.title"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center">
            <NewspaperIcon class="w-24 h-24 text-gray-500" />
          </div>
          <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent"></div>
          
          <!-- Content -->
          <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
            <!-- Category -->
            <RouterLink
              v-if="post.category_name"
              :to="`/categories/${post.category}`"
              class="inline-block px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded-full text-xs font-medium mb-2 transition"
            >
              {{ post.category_name }}
            </RouterLink>
            
            <!-- Title -->
            <RouterLink :to="`/posts/${post.slug}`">
              <h3 class="text-xl font-bold mb-2 drop-shadow-lg line-clamp-2 hover:text-blue-300 transition">
                {{ post.title }}
              </h3>
            </RouterLink>
            
            <!-- Excerpt -->
            <p class="text-sm mb-3 drop-shadow-md line-clamp-2 text-gray-200">
              {{ post.excerpt || truncateText(post.content, 80) }}
            </p>
            
            <!-- Meta Info -->
            <div class="flex items-center gap-3 text-xs text-gray-300">
              <div class="flex items-center gap-1">
                <UserCircleIcon class="w-4 h-4" />
                <span>{{ post.author_username }}</span>
              </div>
              <div class="flex items-center gap-1">
                <EyeIcon class="w-4 h-4" />
                <span>{{ post.views_count || 0 }}</span>
              </div>
              <!-- кнопка лайка -->
              <LikeButton
                content-type="post"
                :object-id="post.id"
                :initial-likes-count="post.likes_count || 0"
                :initial-is-liked="post.is_liked || false"
              />
            </div>
            
            <!-- Button -->
            <RouterLink
              :to="`/posts/${post.slug}`"
              class="inline-block mt-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium transition transform hover:scale-105"
            >
              Читати →
            </RouterLink>
          </div>
        </article>
      </SwiperSlide>
    </Swiper>

    <!-- Custom Navigation Arrows -->
    <button
      class="swiper-button-prev-custom absolute left-2 md:left-4 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-2 md:p-3 rounded-full transition z-10"
      aria-label="Попередній слайд"
    >
      <ChevronLeftIcon class="w-5 h-5 md:w-6 md:h-6" />
    </button>
    
    <button
      class="swiper-button-next-custom absolute right-2 md:right-4 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white p-2 md:p-3 rounded-full transition z-10"
      aria-label="Наступний слайд"
    >
      <ChevronRightIcon class="w-5 h-5 md:w-6 md:h-6" />
    </button>

    <!-- Custom Pagination -->
    <div class="swiper-pagination-custom flex justify-center gap-2 mt-4"></div>
  </div>
</template>

<script setup>
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Navigation, Pagination, Autoplay } from 'swiper/modules'
import { RouterLink } from 'vue-router'
import { 
  ChevronLeftIcon, 
  ChevronRightIcon,
  UserCircleIcon,
  EyeIcon,
  NewspaperIcon
} from '@heroicons/vue/24/outline'
import LikeButton from '@/components/ui/LikeButton.vue'

// Import Swiper styles
import 'swiper/css'
import 'swiper/css/navigation'
import 'swiper/css/pagination'

const props = defineProps({
  posts: {
    type: Array,
    required: true,
    default: () => []
  },
  autoplay: {
    type: Boolean,
    default: true
  },
  interval: {
    type: Number,
    default: 5000
  }
})

const modules = [Navigation, Pagination, Autoplay]

const truncateText = (text, length) => {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}
</script>

<style scoped>
/* Кастомні стилі для Swiper pagination */
:deep(.swiper-pagination-custom .swiper-pagination-bullet) {
  width: 8px;
  height: 8px;
  background: rgb(209, 213, 219);
  opacity: 1;
  transition: all 0.3s;
}

:deep(.swiper-pagination-custom .swiper-pagination-bullet-active) {
  width: 32px;
  background: rgb(37, 99, 235);
  border-radius: 4px;
}

/* Dark mode */
:deep(.dark .swiper-pagination-custom .swiper-pagination-bullet) {
  background: rgb(75, 85, 99);
}

:deep(.dark .swiper-pagination-custom .swiper-pagination-bullet-active) {
  background: rgb(96, 165, 250);
}

/* Ховаємо стандартні кнопки Swiper */
:deep(.swiper-button-next),
:deep(.swiper-button-prev) {
  display: none;
}
</style>