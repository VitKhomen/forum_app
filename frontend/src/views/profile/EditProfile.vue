<script setup lang="ts">
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProfileStore } from '@/stores/useProfile'

const router = useRouter()
const auth = useAuth()

const profileStore = useProfileStore()

const form = reactive({
  username: '',
  email: '',
  avatar: null as File | null
})

async function initProfile() {
  await auth.getSession()
  if (auth.status.value !== 'authenticated') {
    return navigateTo('/login')
  }

  await profileStore.fetchProfile(auth)

  if (profileStore.profile) {
    form.username = profileStore.profile.username
    form.email = profileStore.profile.email
  }
}

onMounted(() => {
  initProfile()
})

async function saveProfile() {
  const data = new FormData()
  data.append('username', form.username)
  data.append('email', form.email)
  if (form.avatar) {
    data.append('avatar', form.avatar)
  }

  try {
    await profileStore.updateProfile(auth, data)
    router.push('/profile')
  } catch (e) {
    console.error('Помилка при збереженні профіля:', e)
    alert('Не вдалося зберегти профіль')
  }
}
</script>

<template>
  <div class="container mt-5">
    <h1>Редагування профіля</h1>
    <form @submit.prevent="saveProfile">
      <div class="mb-3">
        <label class="form-label">Ім'я профіля</label>
        <input v-model="form.username" class="form-control" />
      </div>

      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="form.email" class="form-control" type="email" />
      </div>

      <div class="mb-3">
        <label class="form-label">Аватар</label>
        <input type="file"
               @change="e => form.avatar = (e.target as HTMLInputElement).files?.[0] || null"
               class="form-control" />
      </div>

      <button type="submit" class="btn btn-success">Зберегти</button>
    </form>
  </div>
</template>