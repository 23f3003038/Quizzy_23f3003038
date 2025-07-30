<template>
  <!-- blur-wrapper applies blur when modal is open -->
  <div :class="{ 'blur-wrapper': showInstructions }">
    <div class="container py-4">
      <!-- Back Button -->
      <div class="mb-3 d-flex align-items-center gap-2 text-primary cursor-pointer fw-medium" @click="goBack">
        <i class="bi bi-arrow-left" style="color:#337665"></i>
        Back
      </div>

      <!-- Breadcrumb -->
      <div class="mb-4">
        <small class="text-muted">
          Subject/ <strong>{{ subjectName || '...' }}</strong>/ 
          <strong>{{ chapterName || '...' }}</strong> /
          <strong>{{ quiz.name || '...' }}</strong>
        </small>
      </div>

      <!-- Quiz Info Box -->
      <div class="container-1 p-4 rounded shadow-sm" style="background-color: #f9f9f9">
        <h5 class="fw-bold mb-3">{{ quiz.name }}</h5>
        <p><strong>Description:</strong> {{ quiz.description && quiz.description !== 'None' ? quiz.description : 'N/A' }}</p>
        <p><strong>Deadline:</strong> {{ formatDate(quiz.deadline) }}</p>
        <p><strong>Duration:</strong> {{ formatDuration(quiz.duration) }}</p>
        <p><strong>No. of Questions:</strong> {{ quiz.questions?.length || 0 }}</p>
        <p><strong>Remarks:</strong> {{ quiz.remarks && quiz.remarks !== 'None' ? quiz.remarks : 'N/A' }}</p>

        <!-- Toggle modal instead of direct navigation -->
        <button class="btn mt-3" :style="startQuizButtonStyle" @click="showInstructions = true">
          Start Quiz
        </button>
      </div>
    </div>
  </div>

  <!-- Instructions Modal -->
  <UserQuizInstructions
    v-if="showInstructions && quiz.id"
    :quiz="quiz"
    @close="showInstructions = false"
    @start="onStart"
  />
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import UserQuizInstructions from './user-quiz-instructions.vue'

const router     = useRouter()
const route      = useRoute()
const quizId     = route.params.quizId
const quiz       = ref({ questions: [] })
const subjectName= ref('')
const chapterName= ref('')
const showInstructions = ref(false)

// styling for blur
const blurWrapper = computed(() => showInstructions.value)

function goBack() {
  router.back()
}

function onStart() {
  showInstructions.value = false
  router.push(`/user/quiz/${quizId}/attempt/live`)
}

function fetchQuizDetails() {
  axios.get(`/api/user/quizzes/${quizId}`)
    .then(res => {
      quiz.value = { ...res.data, questions: res.data.questions || [] }

      // fetch chapter name
      return axios.get(`/api/user/chapters/${res.data.chapter_id}`)
    })
    .then(chapRes => {
      chapterName.value = chapRes.data.name
      // fetch subject name
      return axios.get(`/api/user/subjects/${chapRes.data.subject_id}`)
    })
    .then(subjRes => {
      subjectName.value = subjRes.data.name
    })
    .catch(err => console.error(err.response?.data || err.message))
}

function formatDate(dateStr) {
  if (!dateStr || dateStr === 'None') return "N/A"
  const d = new Date(dateStr)
  if (isNaN(d)) return "N/A"
  return d.toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata', year:'numeric', month:'short', day:'numeric' })
}

function formatDuration(durationStr) {
  if (!durationStr || durationStr === 'None') return "N/A"
  const [h, m] = durationStr.split(':').map(Number)
  if (!h && !m) return "0 min"
  return h ? `${h}h ${m} min` : `${m} min`
}

onMounted(fetchQuizDetails)

// button gradient style
const startQuizButtonStyle = computed(() => ({
  background: 'linear-gradient(to right, #fac126, #337665)',
  color: '#fff',
  border: 'none',
  padding: '10px 20px',
  fontWeight: '600',
  borderRadius: '5px',
}))
</script>

<style scoped>
/* blur the background when the modal is active */
.blur-wrapper {
  filter: blur(4px);
  pointer-events: none;
  user-select: none;
}

/* your existing styles… */
.btn:hover {
  background: #337665;
  color: #fac126;
  border-color: #337665;
}
.container {
  max-width: 100vw;
}
.container-1 {
  margin-left: 12rem;
  max-width: 50vw;
}
p {
  margin-bottom: 10px;
}
</style>
