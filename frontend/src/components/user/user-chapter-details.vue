<template>
  <div class="container py-4">
    <!-- Back Button -->
    <div class="mb-3 d-flex align-items-center gap-2 text-primary cursor-pointer fw-medium" @click="goBack">
      <i class="bi bi-arrow-left" style="color:#337665"></i>
      Back
    </div>

    <!-- Breadcrumb -->
    <div class="mb-4">
      <small class="text-muted">Chapter / <strong>{{ chapter?.name || 'Chapter Name' }}</strong></small>
    </div>

    <!-- Chapter Header -->
    <div class="d-flex align-items-center gap-3 mb-4">
      <div class="initials-box">
        {{ chapterInitials }}
      </div>
      <div>
        <h5 class="fw-bold mb-1">{{ chapter?.name }}</h5>
        <p class="text-muted mb-0">{{ chapter?.description }}</p>
      </div>
    </div>

    <!-- Quizzes Table -->
    <h5 class="fw-bold mb-3">Quizzes</h5>
    <div class="table-responsive">
      <table class="table table-hover table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th>Quiz Name</th>
            <th>Deadline</th>
            <th>Duration</th>
            <th>Remarks</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quiz in quizzes" :key="quiz.id">
            <td>Quiz {{ quiz.id }}</td>
            <td>{{ quiz.deadline?.split('T')[0] }}</td>
            <td>{{ quiz.duration_minutes }} min</td>
            <td>{{ quiz.remarks }}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary" @click="viewQuiz(quiz.id)">
                View
              </button>
            </td>
          </tr>
          <tr v-if="quizzes.length === 0">
            <td colspan="4" class="text-center text-muted">No quizzes found.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const chapterId = route.params.id
const chapter = ref({})
const quizzes = ref([])

const chapterInitials = computed(() => {
  const name = chapter.value?.name || ''
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

function viewQuiz(quizId) {
  router.push(`/user/quiz/${quizId}`)
}

function goBack() {
  router.back()
}

function fetchChapterDetails() {
  axios.get(`/api/user/chapters/${chapterId}`).then(res => {
    chapter.value = res.data
    quizzes.value = res.data.quizzes || []
  }).catch(err => {
    console.error('❌ Failed to fetch chapter details', err.response?.data || err.message)
  })
}

onMounted(() => {
  fetchChapterDetails()
})
</script>

<style scoped>
.initials-box {
  background-color: #337665;
  color: white;
  font-weight: bold;
  width: 100px;
  height: 70px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
}
.btn:hover{
    background: #337665;
    color: #fac126;
    border-color: #337665
}
</style>
