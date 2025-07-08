<template>
  <div class="container py-4">
    <!-- Back Button -->
    <div class="mb-3 d-flex align-items-center gap-2 text-primary cursor-pointer fw-medium" @click="goBack">
      <i class="bi bi-arrow-left" style="color:#337665"></i>
      Back
    </div>

    <!-- Breadcrumb -->
    <div class="mb-4">
      <small class="text-muted">Subject/ <strong>{{ subjectName || '...' }}</strong>/ <strong>{{ chapterName || '...' }}</strong> /<strong>{{ quiz.name || '...' }}</strong></small>
    </div>

    <!-- Quiz Info Box -->
    <div class="p-4 rounded shadow-sm" style="background-color: #f9f9f9">
      <h5 class="fw-bold mb-3">{{ quiz.name }}</h5>
      <p><strong>Description:</strong> {{ quiz.description && quiz.description !== 'None' ? quiz.description : 'N/A' }}</p>
      <p><strong>Deadline:</strong> {{ formatDate(quiz.deadline) }}</p>
      <p><strong>Duration:</strong> {{ formatDuration(quiz.duration) }}</p>
      <p><strong>No. of Questions:</strong> {{ quiz.questions?.length || 0 }}</p>
      <p><strong>Remarks:</strong> {{ quiz.remarks && quiz.remarks !== 'None' ? quiz.remarks : 'N/A' }}</p>

      <button class="btn mt-3" :style="startQuizButtonStyle" @click="goToInstructions">
        Start Quiz
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const quizId = route.params.quizId
const quiz = ref({ question:[] })
const subjectName = ref("")
const chapterName = ref("")

const startQuizButtonStyle = computed(() => {
  return {
    background: 'linear-gradient(to right, #fac126, #337665)',
    color: '#fff',
    border: 'none',
    padding: '10px 20px',
    fontWeight: '600',
    borderRadius: '5px',
  };
})

function goBack() {
  router.back()
}

function goToInstructions() {
  router.push(`/user/quiz/${quizId}/attempt`)
}

function fetchQuizDetails() {
  // console.log("📌 Fetching quiz details for ID:", quizId)

  axios.get(`/api/user/quizzes/${quizId}`).then(res => {
    // console.log("✅ Quiz data:", res.data)
    quiz.value = {
        ...res.data,
        questions: res.data.questions || []
    }

    axios.get(`/api/user/chapters/${res.data.chapter_id}`).then(chapterRes => {
      chapterName.value = chapterRes.data.name
      // console.log("📘 Chapter data:", chapterRes.data)

      axios.get(`/api/user/subjects/${chapterRes.data.subject_id}`).then(subjectRes => {
        subjectName.value = subjectRes.data.name
        // console.log("📗 Subject data:", subjectRes.data)
      }).catch(err => console.error("❌ Subject fetch error:", err.response?.data || err.message))
    }).catch(err => console.error("❌ Chapter fetch error:", err.response?.data || err.message))
  }).catch(err => {
    console.error("❌ Quiz fetch error:", err.response?.data || err.message)
  })
}

function formatDate(dateStr) {
  if (!dateStr || dateStr === 'None') return "N/A";

  const date = new Date(dateStr);
  if (isNaN(date)) return "N/A";

  return date.toDateString(); // e.g., "Mon Jul 07 2025"
}


function formatDuration(durationStr) {
  if (!durationStr || durationStr === 'None') return "N/A";

  const parts = durationStr.split(':');
  if (parts.length < 2) return "N/A";

  const h = parseInt(parts[0]);
  const m = parseInt(parts[1]);

  if (!h && !m) return "0 min";
  if (!h) return `${m} min`;
  return `${h}h ${m} min`;
}

onMounted(() => {
  fetchQuizDetails()
})
</script>

<style scoped>
.btn:hover {
  background: #337665;
  color: #fac126;
  border-color: #337665;
}

.container {
  max-width: 100vw;
}

p {
  margin-bottom: 10px;
}
</style>
