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
        <button class="btn btn-outline-success" @click="exportHistory">
          Export Quiz History (CSV)
        </button>
      </div>
    </div>

    <!-- Stats Summary -->
    <div class="row g-3 mb-4">
      <div class="col-md-3 d-flex" v-for="(stat, index) in stats" :key="index">
        <div class="card stat-box text-center shadow-sm p-3 flex-fill">
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
        <tr v-for="attempt in history" :key="attempt.id">
          <td>{{ attempt.title }}</td>
          <td>{{ attempt.score }}</td>
          <td>{{ attempt.accuracy }}</td>
          <td>{{ attempt.completed_at_ist }}</td>
          <td>
            <button class="btn btn-sm btn-outline-primary" @click="viewResult(attempt.id)">
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
    <!-- Pagination Controls -->
    <nav aria-label="History pagination" class="d-flex justify-content-center mt-3"> 
      <ul class="pagination mb-0">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <button class="page-link" 
                  @click="changePage(currentPage - 1)" 
                  :disabled="currentPage === 1">
            Previous
          </button>
        </li>
        <li class="page-item disabled">
          <span class="page-link">
            Page {{ currentPage }} of {{ totalPages }}
          </span>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <button class="page-link" 
                  @click="changePage(currentPage + 1)" 
                  :disabled="currentPage === totalPages">
            Next
          </button>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()

function formatToIST(utcString) {
  const date = new Date(utcString)
  return date.toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

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

// Pagination state
const currentPage = ref(1)         
const perPage     = ref(10)         
const totalPages  = ref(1)

function fetchDashboardData() {
  axios.get('/api/user/dashboard').then(res => {
    const data = res.data
    stats.value = [
      { label: 'Quizzes Taken', value: data.total_quizzes || 0 },
      { label: 'Avg. Score', value: data.average_score + '%' },
      { label: 'Accuracy', value: data.accuracy + '%' },
      { label: 'Last Active', value: data.last_active ? formatToIST(data.last_active) : '-' },
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


function fetchHistory(page = 1) {
  axios.get('/api/user/history', {
    params: { 
      page: page,                  
      per_page: perPage.value      
    }
  })
    .then(res => {
      const data = res.data
      let items = []
      if (Array.isArray(data)) {
        items = data
      } else if (Array.isArray(data.results)) {
        items = data.results                 
      } else if (Array.isArray(data.history)) {
        items = data.history
      } else {
        console.warn('Unexpected history payload:', data)
      }

      // Now safe to .map
      history.value = items.map(item => ({
        ...item,
        completed_at_ist: formatToIST(item.completed_at)
      }))
      currentPage.value = data.page        
      totalPages.value  = data.total_pages
    })
    .catch(err => {
      console.error('❌ Failed to load history', err)
    })
}

function changePage(newPage) {
  if (newPage < 1 || newPage > totalPages.value) return
  fetchHistory(newPage)
}

function viewResult(attemptId) {
  router.push({ name: 'UserQuizResult', params: { attemptId } })
}

function exportHistory() {
  axios.post('/api/user/history/export')
    .then(() => {
      alert('✅ Export started! You will receive your quiz history via email shortly.')
    })
    .catch((err) => {
      console.error('❌ Export failed:', err)
      alert('Something went wrong while requesting the export.')
    })
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
  font-size: 1.2rem;
  font-weight: bold;
  color: #14518f;
}

.stat-label {
  font-size: 1.5rem;
}
</style>
