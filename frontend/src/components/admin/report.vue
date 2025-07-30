<template>
  <div class="container py-4">
    <!-- Title -->
    <h2 class="mb-4">Reports</h2>

    <!-- 1) Top summary cards -->
    <div class="row row-cols-1 row-cols-md-4 g-3 mb-5">
      <div class="col" v-for="card in summaryCards" :key="card.label">
        <div class="card text-center p-3 shadow-sm">
          <div class="h5 text-muted">{{ card.label }}</div>
          <div class="h2">{{ card.value }}</div>
        </div>
      </div>
    </div>

    <!-- 2) Subject‑wise performance & Qualification distribution -->
    <div class="row g-4 mb-5">
      <div class="col-md-6">
        <div class="card p-3 shadow-sm h-100">
          <h5 class="card-title">Subject‑wise Performance</h5>
          <BarChart
            v-if="subjectChartData"
            :data="subjectChartData"
            :options="subjectChartOptions"
          />
          <div v-else class="text-center text-muted py-5">No data.</div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card p-3 shadow-sm h-100">
          <h5 class="card-title">Qualification Distribution</h5>
          <DoughnutChart
            v-if="qualChartData"
            :data="qualChartData"
            :options="qualChartOptions"
          />
          <div v-else class="text-center text-muted py-5">No data.</div>
        </div>
      </div>
    </div>

    <!-- 3) Performance distribution & Student activity -->
    <div class="row g-4">
      <div class="col-md-6">
        <div class="card p-3 shadow-sm h-100">
          <h5 class="card-title">Performance Distribution</h5>
          <BarChart
            v-if="perfDistData"
            :data="perfDistData"
            :options="perfDistOptions"
          />
          <div v-else class="text-center text-muted py-5">No data.</div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card p-3 shadow-sm h-100">
          <h5 class="card-title">Student Activity</h5>
          <DoughnutChart
            v-if="activityData"
            :data="activityData"
            :options="activityOptions"
          />
          <div v-else class="text-center text-muted py-5">No data.</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { Bar, Doughnut } from 'vue-chartjs'

const BarChart      = Bar
const DoughnutChart = Doughnut

// summary counts
const totalStudents = ref(0)
const totalSubjects = ref(0)
const totalChapters = ref(0)
const totalQuizzes  = ref(0)

// raw data
const users    = ref([])
const subjects = ref([])
const scores   = ref([])

// 1️⃣ summary cards
const summaryCards = computed(() => [
  { label: 'Total Students',  value: totalStudents.value },
  { label: 'Total Subjects',  value: totalSubjects.value },
  { label: 'Total Chapters',  value: totalChapters.value },
  { label: 'Total Quizzes',   value: totalQuizzes.value },
])

// 2️⃣ Subject‑wise Performance
const subjectChartData = computed(() => {
  if (!subjects.value.length || !scores.value.length) return null
  const bySub = subjects.value.map(s => {
    const subScores = scores.value.filter(r => r.subject === s.name)
    const avg = subScores.length
      ? +(subScores.reduce((sum,r)=>sum + r.accuracy_num,0) / subScores.length).toFixed(1)
      : 0
    const studentCount = new Set(subScores.map(r=>r.user_id)).size
    return { name: s.name, avg, studentCount }
  })
  return {
    labels: bySub.map(x => x.name),
    datasets: [
      {
        type: 'bar',
        label: 'Avg Score (%)',
        data: bySub.map(x => x.avg),
        backgroundColor: 'rgba(75,192,192,0.5)',
        yAxisID: 'y1'
      },
      {
        type: 'line',
        label: 'Students',
        data: bySub.map(x => x.studentCount),
        borderColor: 'rgba(54, 162, 235, 0.8)',
        fill: false,
        tension: 0.3,
        yAxisID: 'y2'
      }
    ]
  }
})
const subjectChartOptions = {
  responsive: true,
  scales: {
    y1: {
      type: 'linear',
      position: 'left',
      beginAtZero: true,
      max: 100,
      title: { display: true, text: 'Avg Score (%)' }
    },
    y2: {
      type: 'linear',
      position: 'right',
      beginAtZero: true,
      title: { display: true, text: 'Students' },
      grid: { drawOnChartArea: false }
    }
  },
  plugins: { tooltip: { mode: 'index', intersect: false } }
}

// 2️⃣ Qualification Distribution
const qualChartData = computed(() => {
  if (!users.value.length) return null
  const map = {}
  users.value.forEach(u => {
    if (!u.is_admin) map[u.qualification] = (map[u.qualification] || 0) + 1
  })
  return {
    labels: Object.keys(map),
    datasets: [{ data: Object.values(map), backgroundColor: ['#8e5ea2','#3cba9f','#e8c3b9','#c45850'] }]
  }
})
const qualChartOptions = { responsive: true, plugins: { legend: { position: 'right' } } }

// 3️⃣ Performance Distribution
const perfDistData = computed(() => {
  if (!scores.value.length) return null
  const buckets = { 'Above 80':0, '50–80':0, 'Below 50':0 }
  scores.value.forEach(r => {
    const v = r.accuracy_num
    if (v > 80) buckets['Above 80']++
    else if (v >= 50) buckets['50–80']++
    else buckets['Below 50']++
  })
  return {
    labels: Object.keys(buckets),
    datasets: [{ label: 'Students', data: Object.values(buckets), backgroundColor: ['#3e95cd','#8e5ea2','#3cba9f'] }]
  }
})
const perfDistOptions = { responsive: true, scales: { y: { beginAtZero: true, title: { display:true, text:'Students'} } } }

// 3️⃣ Student Activity
const activityData = computed(() => {
  if (!users.value.length || !scores.value.length) return null

  const now = Date.now()
  let active = 0, inactive = 0

  // build a map of user_id -> most recent timestamp
  const lastByUser = scores.value.reduce((map, r) => {
    const ts = new Date(r.timestamp).getTime()
    map[r.user_id] = Math.max(map[r.user_id]||0, ts)
    return map
  }, {})

  users.value.forEach(u => {
    if (!u.is_admin) {
      const last = lastByUser[u.id] || 0
      if (now - last < 1000*60*60*24*7) active++
      else inactive++
    }
  })

  return {
    labels: ['Active (7d)','Inactive'],
    datasets: [{ data: [active,inactive], backgroundColor: ['#8e5ea2','#e8c3b9'] }]
  }
})
const activityOptions = { responsive: true, plugins: { legend: { position:'right' } } }

// fetch everything on mount, but each in its own try/catch
onMounted(async () => {
  // Fetch users
  try {
    const { data } = await axios.get('/api/admin/users')
    users.value = data
    totalStudents.value = data.filter(u => !u.is_admin).length
  } catch (err) {
    console.error('Failed to load users:', err)
  }

  // Fetch subjects
  try {
    const { data } = await axios.get('/api/admin/subjects')
    subjects.value = data
    totalSubjects.value = data.length
  } catch (err) {
    console.error('Failed to load subjects:', err)
  }

  // Count chapters
  try {
    let count = 0
    for (const sub of subjects.value) {
      const { data } = await axios.get(`/api/admin/subjects/${sub.id}/chapters`)
      count += data.length
    }
    totalChapters.value = count
  } catch (err) {
    console.error('Failed to load chapters:', err)
  }

  // Fetch quizzes
  try {
    const { data } = await axios.get('/api/admin/quizzes')
    totalQuizzes.value = data.length
  } catch (err) {
    console.error('Failed to load quizzes:', err)
  }

  // Fetch scores (optional — if this fails, we skip the performance charts)
  try {
    const { data } = await axios.get('/api/admin/scores')
      scores.value = data.map(r => ({
        ...r,
        // your endpoint already returns accuracy_num as a number
        accuracy_num: r.accuracy_num,
        // carry the subject_name over into “subject” so your computed() will pick it up
        subject:      r.subject_name
    }))
  } catch (err) {
    console.warn('Scores endpoint failed, skipping performance charts:', err)
  }
})
</script>

<style scoped>
.card-title {
  font-size: 1.1rem;
  font-weight: 600;
}
</style>
