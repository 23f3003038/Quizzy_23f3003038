<template>
  <div class="container py-4 quiz-result">

    <!-- Back Button -->
    <div class="mb-2">
      <button class="btn btn-link p-0 text-decoration-none" @click="router.back()">
        ← Back
      </button>
    </div>

    <!-- Breadcrumb -->
    <nav class="breadcrumb mb-4">
      <span class="breadcrumb-item">{{ subjectName }}</span>
      <span class="breadcrumb-item">{{ chapterName }}</span>
      <span class="breadcrumb-item">{{ quizTitle }}</span>
      <span class="breadcrumb-item active" aria-current="page"><strong>Report</strong></span>
    </nav>

    <h2 class="mb-4 text-center">📊 Quiz Summary Report</h2>

    <div class="alert alert-info text-center fw-bold">
      You got {{ score.correct }} out of {{ score.total }} correct ({{ accuracy }}%)!
    </div>

    <div class="mb-3 text-center text-muted">
      Completed At: {{ formatToIST(completedAt) }}
    </div>

    <!-- Questions Review -->
    <div
      v-for="(q, index) in questions"
      :key="q.question_id"
      class="mb-4 p-3 border rounded shadow-sm bg-white"
    >
      <p class="fw-semibold">
        Q{{ index + 1 }}. {{ q.question_statement }}
      </p>

      <div class="d-flex flex-column gap-2 mt-2">
        <div
          v-for="(opt, i) in q.options"
          :key="i"
          class="px-3 py-2 rounded"
          :class="optionClass(q, i + 1)"
        >
          <strong>{{ String.fromCharCode(65 + i) }}.</strong> {{ opt }}
          <span v-if="q.selected === i + 1" class="ms-2 badge bg-primary">Your Answer</span>
          <span v-if="q.correct_option === i + 1" class="ms-2 badge bg-success">Correct</span>
        </div>
      </div>

      <div v-if="q.explanation" class="mt-2 text-muted small">
        💡 {{ q.explanation }}
      </div>
    </div>

    <div class="text-center">
      <router-link class="btn btn-secondary mt-3" to="/user/dashboard">🔙 Back to Dashboard</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const scoreId = route.params.scoreId

const score = ref({ correct: 0, total: 0 })
const accuracy = ref(0)
const questions = ref([])
const completedAt = ref(null)

const quizTitle = ref('')
const chapterName = ref('')
const subjectName = ref('')

onMounted(() => {
  fetchReport()
})

function fetchReport() {
  axios.get(`/api/user/scores/${scoreId}/report`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`
    }
  })
  .then(res => {
    const data = res.data

    score.value.correct = data.total_score
    score.value.total = data.total_questions
    accuracy.value = ((data.total_score / data.total_questions) * 100).toFixed(1)
    completedAt.value = data.completed_at

    quizTitle.value = data.quiz_name || 'Quiz'
    chapterName.value = data.chapter_name || 'Chapter'
    subjectName.value = data.subject_name || 'Subject'

    questions.value = data.questions.map(q => ({
      ...q,
      options: Array.isArray(q.options)
        ? q.options
        : (q.options ? q.options.split('\n').map(opt => opt.trim()) : [])
    }))
  })
  .catch(err => {
    console.error('❌ Failed to load quiz report:', err)
    alert("Failed to load quiz report.")
    router.push('/user/dashboard')
  })
}

function formatToIST(utcString) {
  if (!utcString) return '-'
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

function optionClass(q, optionNumber) {
  if (q.selected === optionNumber && q.correct_option !== optionNumber) {
    return 'bg-danger text-white border'
  }
  if (q.correct_option === optionNumber) {
    return 'bg-success text-white border'
  }
  return 'border'
}
</script>

<style scoped>
.quiz-result {
  max-width: 900px;
  margin: auto;
}

.badge {
  font-size: 0.75rem;
}

.bg-success {
  background-color: #28a745 !important;
}

.bg-danger {
  background-color: #dc3545 !important;
}

.bg-primary {
  background-color: #007bff !important;
}

.breadcrumb {
  font-size: 0.9rem;
  color: #6c757d;
}
</style>
