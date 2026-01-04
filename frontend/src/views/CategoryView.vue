<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">
      Категорія: {{ categoryName }}
    </h1>
    <p class="text-gray-600 dark:text-gray-400">Пости категорії будуть тут...</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const categoryName = ref('')

onMounted(() => {
  categoryName.value = route.params.slug
})
</script>