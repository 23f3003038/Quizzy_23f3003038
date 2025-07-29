<template>
  <div class="container py-4">
    <!-- Back + Title -->
    <div class="mb-3 d-flex align-items-center back-button" @click="goBack">
      <i class="bi bi-arrow-left me-2"></i> Back
    </div>
    <h2 class="mb-4">Report</h2>

    <!-- 1) Subject‑wise & Recent Performance -->
    <div class="row g-4 mb-4">
      <!-- Subject‑wise -->
      <div class="col-md-6">
        <div class="card p-3 shadow-sm">
          <h4 class="card-title">Subject‑wise Performance</h4>
          <BarChart
            v-if="subjectChartData"
            :data="subjectChartData"
            :options="subjectChartOptions"
          />
          <div v-else class="text-center text-muted py-5">
            No data.
          </div>
        </div>
      </div>
      <!-- Recent -->
      <div class="col-md-6">
        <div class="card p-3 shadow-sm">
          <h4 class="card-title">Recent Quiz Performance</h4>
          <LineChart
            v-if="recentChartData"
            :data="recentChartData"
            :options="recentChartOptions"
          />
          <div v-else class="text-center text-muted py-5">
            No data.
          </div>
        </div>
      </div>
    </div>

    <!-- 2) Monthly Performance Overview -->
    <div class="mb-4">
      <h4 class="mb-3">Monthly Performance Overview</h4>
      <!-- Cards -->
      <div class="row row-cols-1 row-cols-md-3 g-3 mb-3">
        <div class="col" v-for="card in monthlyCards" :key="card.label">
          <div class="card text-center p-3 shadow-sm">
            <div class="h4 mb-1">{{ card.value }}</div>
            <div class="text-muted">{{ card.label }}</div>
          </div>
        </div>
      </div>
      <!-- Chart -->
      <div class="card p-3 shadow-sm">
        <LineChart
          v-if="monthlyChartData"
          :data="monthlyChartData"
          :options="monthlyChartOptions"
        />
        <div v-else class="text-center text-muted py-5">
          Not enough data.
        </div>
      </div>
    </div>

    <div class="card p-3 shadow-sm mb-4">
      <h4 class="card-title">Leaderboard</h4>
      <table class="table">
        <thead><tr><th>#</th><th>Name</th><th>Total Score</th><th>Avg. Accuracy</th></tr></thead>
        <tbody>
          <tr v-if="leaderboard.length === 0">
            <td colspan="4" class="text-center text-muted py-3">No leaderboard data</td>
          </tr>
          <tr v-for="(u,i) in leaderboard" :key="u.user_id">
            <td>{{ i+1 }}</td>
            <td>{{ u.full_name }}</td>
            <td>{{ u.total_score }}</td>
            <td>{{ u.avg_accuracy }}%</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Bar, Line } from 'vue-chartjs'

// Router for Back
const router = useRouter()
function goBack() {
  router.push('/user')
}

const history = ref([])
const leaderboard = ref([])

// Fetch history once
async function fetchHistory() {
  try {
    const res = await axios.get('/api/user/history', { params: { page: 1, per_page: 1000 } })
    const items = Array.isArray(res.data) ? res.data : res.data.results || []
    history.value = items.map(i => ({
      ...i,
      completed_at_ist: new Date(i.completed_at).toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
      }),
      accuracy_num: parseFloat(i.accuracy),
      subject: i.title.split('/')[0].trim()
    }))
  } catch (e) {
    console.error(e)
  }
}

async function fetchLeaderboard() {
  try {
    const res = await axios.get('/api/user/leaderboard')
    leaderboard.value = res.data.map(u => ({
      ...u,
      avg_accuracy: +u.avg_accuracy.toFixed(1)
    }))
  } catch (e) {
    console.error('Failed to fetch leaderboard', e)
  }
}

// Subject‑wise Performance
const subjectChartData = computed(() => {
  if (!history.value.length) return null
  const bySub = {}
  history.value.forEach(({ subject, accuracy_num }) => {
    if (!bySub[subject]) bySub[subject] = []
    bySub[subject].push(accuracy_num)
  })
  const labels = Object.keys(bySub)
  const data = labels.map(s => {
    const arr = bySub[s]
    return +(arr.reduce((sum, a) => sum + a, 0) / arr.length).toFixed(1)
  })
  return { labels, datasets: [{ label: 'Avg. Accuracy', data }] }
})
const subjectChartOptions = {
  responsive: true,
  scales: { y: { beginAtZero: true, max: 100, ticks: { callback: v => v + '%' } } }
}

// Recent Quiz Performance (last 5)
const recentChartData = computed(() => {
  if (history.value.length < 1) return null
  const recent = history.value.slice(-5)
  return {
    labels: recent.map(r => r.title),
    datasets: [{ label: 'Accuracy', data: recent.map(r => r.accuracy_num), tension: 0.3, fill: false }]
  }
})
const recentChartOptions = {
  responsive: true,
  scales: { y: { beginAtZero: true, max: 100 } }
}

// Monthly Performance Overview
const monthly = computed(() => {
  const map = {}
  history.value.forEach(({ completed_at_ist, accuracy_num }) => {
    // month key like 'Jul 2025'
    const m = new Date(completed_at_ist).toLocaleString('en-IN', { month: 'short', year: 'numeric' })
    if (!map[m]) map[m] = []
    map[m].push(accuracy_num)
  })
  return Object.entries(map)
    .sort((a,b)=> new Date(a[0]) - new Date(b[0]))
    .map(([month, arr])=>({
      month,
      avg: +(arr.reduce((s,v)=>s+v,0)/arr.length).toFixed(1),
      count: arr.length,
      best: Math.max(...arr)
    }))
})
// Cards: average, highest, total this month (last month in list)
const monthlyCards = computed(()=> {
  if (!monthly.value.length) return []
  const last = monthly.value.at(-1)
  return [
    { label: `Avg. (${last.month})`, value: last.avg + '%' },
    { label: `Best (${last.month})`, value: last.best + '%' },
    { label: `Quizzes (${last.month})`, value: last.count }
  ]
})
// Line chart of avg over months
const monthlyChartData = computed(()=>{
  if (!monthly.value.length) return null
  return {
    labels: monthly.value.map(m=>m.month),
    datasets: [{ label: 'Avg. Accuracy', data: monthly.value.map(m=>m.avg), fill: false, tension: 0.2 }]
  }
})
const monthlyChartOptions = {
  responsive: true,
  scales: { y: { beginAtZero: true, max: 100, ticks: { callback: v=>v+'%' } } }
}

// Mount and register chart aliases
onMounted(() => {
  fetchHistory()
  fetchLeaderboard()
})

const BarChart  = Bar
const LineChart = Line
</script>

<style scoped>
.card-title {
  font-size: 1.2rem;
  font-weight: 600;
}

.back-button{
  cursor:pointer;
}
</style>
