<template>
  <div class="container py-4">
    <!-- User Info Section -->
    <div class="d-flex align-items-center gap-3 mb-4">
      <img src="/user-logo.png" alt="User" class="user-icon" />
      <div>
        <h4 class="fw-bold mb-1">{{ user?.name }}</h4>
        <p class="text-muted mb-0">Email: {{ user?.email }}</p>
        <p class="text-muted mb-0">Qualification: {{ user.qualification }}</p>
    <p class="text-muted mb-0">DOB: {{ user.dob }}</p>
        <!-- <p class="text-muted mb-0">Student ID: {{ user?.id }}</p> -->
      </div>
    </div>

    <!-- Stats Summary -->
    <div class="row g-3 mb-4">
      <div class="col-md-3" v-for="(stat, index) in stats" :key="index">
        <div class="card stat-box text-center shadow-sm">
          <div class="card-body">
            <div class="stat-value">{{ stat.value }}</div>
            <div class="stat-label text-muted">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- History Section -->
    <h2 class="mb-3 fw-bold">History</h2>
    <div class="table-responsive">
      <table class="table table-hover table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th>Quiz Title</th>
            <th>Score</th>
            <th>Accuracy</th>
            <th>Completion Date</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quiz in history" :key="quiz.id">
            <td>{{ quiz.title }}</td>
            <td>{{ quiz.score }}%</td>
            <td>{{ quiz.accuracy }}%</td>
            <td>{{ quiz.completed_at }}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary" @click="viewReport(quiz.id)">
                View
              </button>
            </td>
          </tr>
          <tr v-if="history.length === 0">
            <td colspan="5" class="text-center text-muted">No quiz history found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

const user = ref({
  name: '',
  email: '',
  qualification: '',
  dob: '',
  // id: '',
})
const stats = ref([
  { label: 'Quizzes Taken', value: 0 },
  { label: 'Avg. Score', value: '0%' },
  { label: 'Accuracy', value: '0%' },
  { label: 'Last Active', value: '-' },
])
const upcomingQuiz = ref(null)
const history = ref([])

function fetchDashboardData() {
  axios.get('/api/user/dashboard').then(res => {
    const data = res.data
    stats.value = [
      { label: 'Quizzes Taken', value: data.total_quizzes || 0 },
      { label: 'Avg. Score', value: data.average_score + '%' },
      { label: 'Accuracy', value: data.accuracy + '%' },
      { label: 'Last Active', value: data.last_active || '-' },
    ]
    user.value = {
      name: data.full_name,
      email: data.email,
      id: data.student_id,
      qualification: data.qualification,
      dob: data.dob 
    }
  }).catch(err => {
    console.error('❌ Failed to load dashboard data', err)
  })
}


function fetchHistory() {
  axios.get('/api/user/history').then(res => {
    history.value = res.data
  }).catch(err => {
    console.error('❌ Failed to load history', err)
  })
}

function viewReport(quizId) {
  router.push(`/user/report/${quizId}`)
}

onMounted(() => {
  fetchDashboardData()
  fetchHistory()
})
</script>

<style scoped>
.user-icon {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #2b7a78;
}

.stat-box {
  background-color: #e0f7f1;
  border-radius: 8px;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #14518f;
}

.stat-label {
  font-size: 0.95rem;
}
</style>
