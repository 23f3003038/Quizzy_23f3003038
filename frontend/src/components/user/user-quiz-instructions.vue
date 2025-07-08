<template>
  <div class="container py-4">
    <!-- Back Button -->
    <div class="mb-3 text-primary cursor-pointer fw-medium" @click="goBack">
      <i class="bi bi-arrow-left" style="color:#337665"></i> Back
    </div>

    <!-- Quiz Title -->
    <h3 class="fw-bold mb-3">{{ quiz.name }}</h3>

    <!-- Quiz Info -->
    <p><strong>Duration:</strong> {{ formatDuration(quiz.duration) }}</p>
    <p><strong>Total Questions:</strong> {{ quiz.questions?.length || 0 }}</p>

    <!-- Rules -->
    <div class="mt-4">
      <h5>Rules:</h5>
      <ul>
        <li>Each question has only one correct answer.</li>
        <li>No negative marking.</li>
        <li>Timer starts once you begin.</li>
      </ul>
    </div>

    <!-- Availability Message -->
    <div v-if="!isAvailable" class="alert alert-warning mt-3">
      ⏳ This quiz can only be attempted before <strong>{{ formatDate(quiz.deadline) }}</strong>.
    </div>

    <!-- Start Button -->
    <button class="btn btn-primary mt-4" @click="startQuiz" :disabled="!isAvailable">
      Start Quiz
    </button>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const quizId = route.params.quizid
const quiz = ref({})
const isAvailable = ref(true)

function goBack() {
  router.back()
}

function formatDuration(durationStr) {
  if (!durationStr || durationStr === 'None') return "N/A"
  const [h, m] = durationStr.split(':')
  return `${parseInt(h)}h ${parseInt(m)}m`
}

function formatDate(utc) {
  if (!utc) return "N/A"
  const date = new Date(utc)
  return date.toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function checkAvailability(dateStr, deadlineStr) {
  if (!dateStr || !deadlineStr) return false

  const now = new Date()
  const start = new Date(dateStr)  // already in UTC
  const end = new Date(deadlineStr)

  return now >= start && now <= end
}

function startQuiz() {
  router.push(`/user/quiz/${quizId}/attempt/live`)
}

onMounted(() => {
  axios.get(`/api/user/quizzes/${quizId}`)
    .then(res => {
      quiz.value = res.data
      isAvailable.value = checkAvailability(quiz.value.date_of_quiz, quiz.value.deadline)
    })
    .catch(err => {
      console.error('❌ Failed to fetch quiz data:', err.response?.data || err.message)
    })
})
</script>

<style scoped>
.container {
  max-width: 100vw;
}
ul {
  padding-left: 18px;
}
</style>
