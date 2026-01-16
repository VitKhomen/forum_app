import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { title: 'Головна' }
    },
    {
      path: '/posts',
      name: 'posts',
      component: () => import('@/views/posts/PostsView.vue'),
      meta: { title: 'Пости' }
    },
     {
      path: '/posts/popular',
      name: 'popular-posts',
      component: () => import('@/views/posts/PopularPostsView.vue'),
      meta: { title: 'Популярні пости' }
    },
    {
      path: '/posts/trending',
      name: 'trending-posts',
      component: () => import('@/views/posts/TrendingPostsView.vue'),
      meta: { title: 'Пости в тренді' }
    },
    {
      path: '/posts/:slug',
      name: 'post-detail',
      component: () => import('@/views/posts/PostDetailView.vue'),
      meta: { title: 'Деталі поста' }
    },
    {
      path: '/categories/:slug',
      name: 'category',
      component: () => import('@/views/CategoryView.vue'),
      meta: { title: 'Категорія' }
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('@/views/SearchView.vue'),
      meta: { title: 'Пошук' }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { 
        title: 'Вхід',
        guest: true 
      }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { 
        title: 'Реєстрація',
        guest: true 
      }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/profile/ProfileView.vue'),
      meta: { 
        title: 'Профіль',
        requiresAuth: true 
      }
    },
    {
      path: '/profile/posts',
      name: 'my-posts',
      component: () => import('@/views/profile/MyPostsView.vue'),
      meta: { 
        title: 'Мої пости',
        requiresAuth: true 
      }
    },
    {
      path: '/profile/create-post',
      name: 'create-post',
      component: () => import('@/views/profile/CreatePostView.vue'),
      meta: { 
        title: 'Створити пост',
        requiresAuth: true 
      }
    },
    {
      path: '/profile/edit-post/:slug',
      name: 'edit-post',
      component: () => import('@/views/profile/EditPostView.vue'),
      meta: { 
        title: 'Редагувати пост',
        requiresAuth: true 
      }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
      meta: { title: 'Про нас' }
    },
    {
      path: '/contact',
      name: 'contact',
      component: () => import('@/views/ContactView.vue'),
      meta: { title: 'Контакти' }
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFoundView.vue'),
      meta: { title: 'Сторінка не знайдена' }
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Set page title
  document.title = `${to.meta.title || 'Форум'} | Forum`

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }

  // Redirect authenticated users from guest pages
  if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'home' })
    return
  }

  next()
})

export default router