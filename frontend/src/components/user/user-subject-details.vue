<template>
  <div class="container py-4">
    <!-- Back Button -->
    <div class="mb-3 d-flex align-items-center gap-2 text-primary cursor-pointer fw-medium" @click="goBack">
      <i class="bi bi-arrow-left" style="color:#337665"></i>
      Back
    </div>

    <!-- Breadcrumb -->
    <div class="mb-4">
      <small class="text-muted">Subject /<strong>{{ subject?.name || 'Subject Name' }}</strong></small>
    </div>

    <!-- Subject Header -->
    <div class="d-flex align-items-center gap-3 mb-4">
      <div class="initials-box">
        {{ subjectInitials }}
      </div>
      <div>
        <h5 class="fw-bold mb-1">{{ subject?.name }}</h5>
        <p class="text-muted mb-0">{{ subject?.description }}</p>
      </div>
    </div>

    <!-- Chapters Table -->
    <h5 class="fw-bold mb-3">Chapters</h5>
    <div class="table-responsive">
      <table class="table table-hover table-bordered align-middle">
        <thead class="table-light">
          <tr>
            <th>Chapter Name</th>
            <th>Description</th>
            <th>Quizzes</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="chapter in chapters" :key="chapter.id">
            <td>{{ chapter.name }}</td>
            <td>{{ chapter.description }}</td>
            <td>{{ chapter.quiz_count }}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary" @click="viewChapter(chapter.id)">
                View
              </button>
            </td>
          </tr>
          <tr v-if="chapters.length === 0">
            <td colspan="4" class="text-center text-muted">No chapters found.</td>
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

const subjectId = route.params.id
const subject = ref({})
const chapters = ref([])

const subjectInitials = computed(() => {
  const name = subject.value?.name || ''
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

function goBack() {
  router.back()
}

function viewChapter(chapterId) {
  router.push(`/user/chapters/${chapterId}/details`)
}

function fetchSubjectDetails() {
  axios.get(`/api/user/subjects/${subjectId}`).then(res => {
    subject.value = res.data
  }).catch(err => {
    console.error('❌ Failed to fetch subject details', err.response?.data || err.message)
  })
}

function fetchChapters() {
  axios.get(`/api/user/subjects/${subjectId}/chapters`).then(res => {
    chapters.value = res.data.map(c => ({
      ...c,
      quiz_count: c.quizzes?.length || 0
    }))
  }).catch(err => {
    console.error('❌ Failed to fetch chapters', err.response?.data || err.message)
  })
}

onMounted(() => {
  fetchSubjectDetails()
  fetchChapters()
})
</script>

<style scoped>
.initials-box {
  background-color: #2b7a78;
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
