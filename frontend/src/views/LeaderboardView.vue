<!-- views/LeaderboardView.vue -->
<template>
  <div class="leaderboard-view">
    <div class="container">
      <h1>🏆 Рейтинг користувачів</h1>

      <!-- Топ 3 (Podium) -->
      <div v-if="topThree.length === 3" class="podium">
        <!-- 2 місце -->
        <div class="podium-item second">
          <div class="medal">🥈</div>
          <div class="rank">2</div>
          <div class="username">{{ topThree[1].username }}</div>
          <KarmaBadge 
            :karma="topThree[1].karma_points" 
            :level="topThree[1].karma_level" 
          />
        </div>

        <!-- 1 місце -->
        <div class="podium-item first">
          <div class="medal">🥇</div>
          <div class="rank">1</div>
          <div class="username">{{ topThree[0].username }}</div>
          <KarmaBadge 
            :karma="topThree[0].karma_points" 
            :level="topThree[0].karma_level" 
            size="large"
          />
        </div>

        <!-- 3 місце -->
        <div class="podium-item third">
          <div class="medal">🥉</div>
          <div class="rank">3</div>
          <div class="username">{{ topThree[2].username }}</div>
          <KarmaBadge 
            :karma="topThree[2].karma_points" 
            :level="topThree[2].karma_level" 
          />
        </div>
      </div>

      <!-- Остальные пользователи -->
      <div class="leaderboard-table">
        <div 
          v-for="(user, index) in restUsers" 
          :key="user.username"
          class="table-row"
        >
          <div class="rank">{{ index + 4 }}</div>
          <router-link :to="`/profile/${user.username}`" class="username">
            {{ user.username }}
          </router-link>
          <KarmaBadge 
            :karma="user.karma_points" 
            :level="user.karma_level" 
            size="small"
          />
        </div>
      </div>

      <div v-if="loading" class="loading">Завантаження...</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useKarma } from '@/composables/useKarma'
import KarmaBadge from '@/components/ui/KarmaBadge.vue'

const { getLeaderboard } = useKarma()

const users = ref([])
const loading = ref(false)

const topThree = computed(() => users.value.slice(0, 3))
const restUsers = computed(() => users.value.slice(3))

const loadLeaderboard = async () => {
  loading.value = true
  try {
    users.value = await getLeaderboard(50)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLeaderboard()
})
</script>

<style scoped>
.leaderboard-view {
  min-height: 100vh;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.container {
  max-width: 1000px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  color: white;
  margin-bottom: 40px;
  font-size: 2.5rem;
}

.podium {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 20px;
  margin-bottom: 40px;
}

.podium-item {
  background: white;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  min-width: 200px;
  position: relative;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.podium-item.first {
  order: 2;
  padding-top: 40px;
  transform: scale(1.1);
}

.podium-item.second {
  order: 1;
  padding-top: 30px;
}

.podium-item.third {
  order: 3;
  padding-top: 30px;
}

.medal {
  font-size: 3rem;
  margin-bottom: 8px;
}

.rank {
  font-size: 1.2rem;
  font-weight: bold;
  color: #6c757d;
  margin-bottom: 8px;
}

.username {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: #010102
}

.leaderboard-table {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
}

.table-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: #f8f9fa;
}

.table-row .rank {
  font-weight: bold;
  min-width: 40px;
  font-size: 1.1rem;
  color: #6c757d;
}

.table-row .username {
  flex: 1;
  font-weight: 600;
  text-decoration: none;
  color: #333;
}

.table-row .username:hover {
  color: #667eea;
}
</style>