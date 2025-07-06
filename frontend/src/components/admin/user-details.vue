<!-- frontend/src/components/admin/user-details.vue -->
<template>
  <div class="p-4">
    <!-- Back Button -->
    <router-link to="/admin/users" class="btn btn-link text-decoration-none mb-3">
      <i class="bi bi-arrow-left me-1"></i> Back
    </router-link>

    <!-- Heading -->
    <h2 class="mb-4">Student Details</h2>

    <div v-if="user" class="card shadow-sm mb-4 p-3 d-flex flex-row align-items-center">
      <!-- Initials Square -->
      <div class="initials-box me-3">
        {{ getInitials(user.full_name) }}
      </div>

      <!-- User Info -->
      <div>
        <h4 class="mb-1">{{ user.full_name }}</h4>
        <p class="mb-1 text-muted">{{ user.qualification || '—' }}</p>
        <p class="mb-0 text-muted">{{ user.dob ? new Date(user.dob).toLocaleDateString() : '—' }}</p>
      </div>
    </div>

    <!-- Summary Stats -->
    <div class="row g-3 mb-5">
      <div class="col-md-4">
        <div class="card text-center shadow-sm p-3">
          <h5>Total Quizzes</h5>
          <p class="display-6 mb-0">{{ stats.totalQuizzes }}</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-center shadow-sm p-3">
          <h5>Average Score</h5>
          <p class="display-6 mb-0">{{ stats.avgScore }}%</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-center shadow-sm p-3">
          <h5>Last Active</h5>
          <p class="mb-0">{{ formatDate(stats.lastActive) || '—' }}</p>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <h4 class="mb-3">Recent Activity</h4>
    <table class="table table-striped">
      <thead>
        <tr>
          <th>Subject</th>
          <th>Quiz</th>
          <th>Score</th>
          <th>Accuracy</th>
          <th>Completion Date</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(entry, idx) in activity" :key="idx">
          <td>{{ entry.subject }}</td>
          <td>{{ entry.quiz }}</td>
          <td>{{ entry.score }}%</td>
          <td>{{ entry.accuracy }}%</td>
          <td>{{ formatDate(entry.completed_at) }}</td>
          <td>
            <button class="btn btn-sm btn-outline-primary custom-hover">View Details</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!user">
      <p>Loading user data...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const userId = route.params.id
const user = ref(null)
const stats = ref({
  totalQuizzes: 0,
  avgScore: 0,
  lastActive: null
})
const activity = ref([])

function getInitials(name) {
  return name
    .split(' ')
    .map(word => word[0]?.toUpperCase())
    .join('')
    .slice(0, 2)
}

function formatDate(dateStr) {
  if (!dateStr) return null
  return new Date(dateStr).toLocaleString()
}

onMounted(async () => {
  try {
    const [userRes, statsRes, activityRes] = await Promise.all([
      axios.get(`/api/admin/users/${userId}`, { withCredentials: true }),
      axios.get(`/api/admin/users/${userId}/stats`, { withCredentials: true }),
      axios.get(`/api/admin/users/${userId}/activity`, { withCredentials: true })
    ])
    user.value = userRes.data
    stats.value = statsRes.data
    activity.value = activityRes.data
  } catch (err) {
    console.error('Failed to load user details:', err)
  }
})
</script>

<style scoped>
.initials-box {
  width: 100px;
  height: 100px;
  background-color: #14518f;
  color: #fff;
  font-size: 24px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
}

.custom-hover:hover {
  background-color:  #0a3158 ;
  color: white ;
  border-color: black ;
}
</style>
