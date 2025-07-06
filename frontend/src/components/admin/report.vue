<template>
  <div>
    <h2 class="mb-4">Reports</h2>

    <!-- Summary Cards -->
    <div class="row g-4 mb-5">
      <div
        class="col-6 col-md-3"
        v-for="(value, title) in counts"
        :key="title"
      >
        <div class="card text-center shadow-sm h-100">
          <div class="card-body d-flex flex-column justify-content-center">
            <h5 class="card-title">{{ title }}</h5>
            <p class="display-5 mb-0">{{ value }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts -->
    <div class="row g-4">
      <!-- Bar Chart -->
      <div class="col-12 col-md-4">
        <div class="card shadow-sm h-100">
          <div class="card-header">Attempts per Subject</div>
          <div class="card-body">
            <canvas id="barChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Donut Chart -->
      <div class="col-12 col-md-4">
        <div class="card shadow-sm h-100">
          <div class="card-header">Quizzes per Chapter</div>
          <div class="card-body">
            <canvas id="donutChart"></canvas>
          </div>
        </div>
      </div>

      <!-- Pie Chart -->
      <div class="col-12 col-md-4">
        <div class="card shadow-sm h-100">
          <div class="card-header">Average Score per Quiz</div>
          <div class="card-body">
            <canvas id="pieChart"></canvas>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Chart from 'chart.js/auto'

const counts = ref({
  'Total Users': 0,
  'Total Subjects': 0,
  'Total Chapters': 0,
  'Total Quizzes': 0
})

onMounted(async () => {
  try {
    // Fetch raw lists for counts
    const [uRes, sRes, qRes, cRes] = await Promise.all([
      axios.get('/api/admin/users'),
      axios.get('/api/admin/subjects'),
      axios.get('/api/admin/quizzes'),
      axios.get('/api/admin/chapters')
    ])
    counts.value['Total Users']    = uRes.data.length
    counts.value['Total Subjects'] = sRes.data.length
    counts.value['Total Quizzes']  = qRes.data.length
    counts.value['Total Chapters'] = cRes.data.length

    // 1. Bar chart: quiz attempts per subject
    const attemptsRes = await axios.get('/api/admin/reports/attempts-per-subject')
    const subjLabels = attemptsRes.data.map(x => x.subject)
    const subjData   = attemptsRes.data.map(x => x.count)
    const barCtx     = document.getElementById('barChart').getContext('2d')
    new Chart(barCtx, {
      type: 'bar',
      data: {
        labels: subjLabels,
        datasets: [{
          label: 'Attempts',
          data: subjData,
          backgroundColor: 'rgba(54, 162, 235, 0.6)'
        }]
      },
      options: { responsive: true }
    })

    // 2. Donut chart: quizzes per chapter
    const qpCRes    = await axios.get('/api/admin/reports/quizzes-per-chapter')
    const chapLabels = qpCRes.data.map(x => x.chapter)
    const chapData   = qpCRes.data.map(x => x.count)
    const donutCtx   = document.getElementById('donutChart').getContext('2d')
    new Chart(donutCtx, {
      type: 'doughnut',
      data: {
        labels: chapLabels,
        datasets: [{
          label: 'Quizzes',
          data: chapData,
          backgroundColor: [
            'rgba(255, 99, 132, 0.6)',
            'rgba(255, 205, 86, 0.6)',
            'rgba(75, 192, 192, 0.6)'
          ]
        }]
      },
      options: { responsive: true }
    })

    // 3. Pie chart: average score per quiz
    const avgRes     = await axios.get('/api/admin/reports/average-score-per-quiz')
    const quizLabels = avgRes.data.map(x => x.quiz)
    const avgData    = avgRes.data.map(x => x.avg_score)
    const pieCtx     = document.getElementById('pieChart').getContext('2d')
    new Chart(pieCtx, {
      type: 'pie',
      data: {
        labels: quizLabels,
        datasets: [{
          label: 'Avg Score',
          data: avgData,
          backgroundColor: [
            'rgba(153, 102, 255, 0.6)',
            'rgba(255, 159, 64, 0.6)',
            'rgba(201, 203, 207, 0.6)'
          ]
        }]
      },
      options: { responsive: true }
    })

  } catch (err) {
    console.error('Failed to load report data:', err)
  }
})
</script>

<style scoped>
.card-header {
  font-weight: 600;
}
</style>
