<template>
  <div class="Overview section">
    <h2 class="mb-4">Dashboard Overview</h2>

    <!-- Summary Cards -->
    <div class="row mb-5">
      <div
        class="col-6 col-md-3"
        v-for="card in cards"
        :key="card.title"
        style="padding: 0.5rem;"
      >
        <router-link :to="card.link" class="text-decoration-none">
          <div
            class="card text-center h-100 shadow-sm hover-pointer"
            style="background: linear-gradient(to bottom, #f8f9fa, #14518f, #000); color:#f8f9fa"
          >
            <div class="card-body d-flex flex-column justify-content-center">
              <i
                :class="card.icon"
                class="mb-2 text-white"
                style="font-size:2.5rem;"
              ></i>
              <h5 class="card-title">{{ card.title }}</h5>
              <p class="display-6 mb-0">{{ card.value }}</p>
            </div>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Recent Activity -->
    <h4 class="mb-3">Recent Activity</h4>
    <ul class="list-group">
      <li
        class="list-group-item d-flex align-items-center"
        v-for="(a, idx) in recent"
        :key="idx"
      >
        <i class="bi bi-check-circle text-success me-2"></i>
        <div>
          <strong>{{ formatDate(a.when) }}</strong> –
          <template v-if="a.type === 'registration'">
            New user registered: <strong>{{ a.user }}</strong>
          </template>
          <template v-else-if="a.type === 'score'">
            {{ a.user }} scored <strong>{{ a.score }}</strong> on quiz #{{ a.quiz }}
          </template>
          <template v-else-if="a.type === 'quiz_created'">
            Quiz "<strong>{{ a.quiz_name }}</strong>" created by {{ a.admin }}
          </template>
          <template v-else>
            {{ a.message || 'Unknown activity' }}
          </template>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const cards = ref([
  { title: 'Users',            icon: 'bi bi-people',          value: 0, link: '/admin/users' },
  { title: 'Subjects',         icon: 'bi bi-journal-bookmark', value: 0, link: '/admin/subjects' },
  { title: 'Upcoming Quizzes', icon: 'bi bi-clock-history',   value: 0, link: '/admin/quizzes' },
  { title: 'Reports',          icon: 'bi bi-bar-chart',       value: '→', link: '/admin/reports' }
])

const recent = ref([])

onMounted(async () => {
  try {
    const [usersRes, quizzesRes, questionsRes, subjectRes, recentRes] = await Promise.all([
      axios.get('/api/admin/users', { withCredentials: true }),
      axios.get('/api/admin/quizzes', { withCredentials: true }),
      axios.get('/api/admin/questions'),
      axios.get('/api/admin/subjects'),
      axios.get('/api/admin/recent-activity')
    ])

    const users = usersRes.data || []
    const nonAdmins = users.filter(u => !u.is_admin)

     const upcomingQuizzes = (quizzesRes.data || []).filter(q => new Date(q.date_of_quiz) > new Date())


    cards.value[0].value = nonAdmins.length
    cards.value[1].value = subjectRes.data?.length || 0
    cards.value[2].value = upcomingQuizzes.length

    // Recent activity from backend
    recent.value = recentRes.data || []
  } catch (e) {
    console.error('Dashboard loading error:', e)
  }
})

function formatDate(isoString) {
  if (!isoString) return '—'
  const date = new Date(isoString)
  return isNaN(date.getTime()) ? 'Invalid Date' : date.toLocaleString()
}
</script>

<style scoped>
.hover-pointer {
  cursor: pointer;
  transition: transform 0.2s ease;
}
.hover-pointer:hover {
  transform: scale(1.03);
  z-index: 2;
  position: relative;
}
.card {
  overflow: hidden;
  border: 1px solid #dee2e6;
}
</style>
