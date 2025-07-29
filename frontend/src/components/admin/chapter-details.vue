<template>
  <div v-if="!isLoaded" class="container py-4 text-center">
    Loading chapter details…
  </div>
  <div class="container py-4">
    <!-- Back -->
    <div class="mb-3 d-flex align-items-center cursor-pointer" @click="goBack">
      <i class="bi bi-arrow-left me-2"></i> Back
    </div>

    <!-- Breadcrumb -->
    <div class="text-muted mb-3">
      Subject / {{ subjectName }} / <strong>{{ chapter?.name }}</strong>
    </div>

    <!-- Chapter Info -->
    <div class="d-flex align-items-start gap-3 mb-4 p-3 border rounded shadow-sm">
      <div class="initials-box">{{ chapterInitials }}</div>
      <div class="flex-grow-1">
        <h4 class="mb-1">{{ chapter?.name }}</h4>
        <p class="text-muted">{{ chapter?.description }}</p>
        <div class="d-flex gap-2 mt-2">
          <button class="btn btn-sm btn-secondary" @click="openChapterForm(chapter)">Edit</button>
          <button class="btn btn-sm btn-danger" @click="deleteChapter">Delete</button>
        </div>
      </div>
    </div>

    <!-- + Create Quiz Button -->
    <div class="mb-3 text-end">
      <button class="btn btn-primary" @click="openQuizForm()">+ Create Quiz</button>
    </div>

    <!-- Quizzes Table -->
    <h5 class="mb-3">Quizzes</h5>
    <div class="table-responsive">
      <table class="table table-hover">
        <thead>
          <tr>
            <th>S.No</th>
            <th>Quiz Name</th>
            <th>Total Time</th>
            <th>Deadline</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredQuizzes.length === 0">
            <td colspan="5" class="text-center text-muted py-4">
               No quizzes found.
            </td>
          </tr>
          <tr v-for="(quiz, index) in filteredQuizzes" :key="quiz.id">
            <td>{{ index + 1 }}</td>
            <td>{{ quiz.name }}</td>
            <td>{{ quiz.duration }}</td>
            <td>{{ quiz.deadline?.substring(0, 10) }}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary me-1" @click="viewQuiz(quiz)">View</button>
              <button class="btn btn-sm btn-outline-secondary me-1" @click="openQuizForm(quiz)">Edit</button>
              <button class="btn btn-sm btn-outline-danger" @click="deleteQuiz(quiz.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Forms -->
    <ChapterForm
      v-if="showChapterForm"
      :chapter="editingChapter"
      :subject-id="chapter?.subject_id"
      :subject-name="subjectName"
      @saved="fetchChapter"
      @close="showChapterForm = false"
    />

    <QuizForm
      v-if="showQuizForm"
      :quiz="editingQuiz"
      :chapter-id="Number(chapterId)"
      @saved="fetchQuizzes"
      @close="showQuizForm = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const props = defineProps({
  id: {
    type: [String, Number],
    required: false
  }
})

// Forms
import QuizForm from './quiz-form.vue'
import ChapterForm from './chapter-form.vue'

const route = useRoute()
const router = useRouter()

const chapterId = props.id ?? route.params.id

const chapter = ref(null)
const quizzes = ref([])
const filteredQuizzes = ref([])
const subjectName = ref(null)

const showChapterForm = ref(false)
const showQuizForm = ref(false)
const editingChapter = ref(null)
const editingQuiz = ref(null)

const isLoaded = computed(() => !!chapter.value && quizzes.value !== null)

const chapterInitials = computed(() => {
  if (!chapter.value?.name) return ""
  return chapter.value.name
    .split(" ")
    .map(word => word[0])
    .join("")
    .substring(0, 2)
    .toUpperCase()
})

function goBack() {
  router.back()
}

function fetchChapter() {
  axios.get(`/api/admin/chapters/${chapterId}`)
    .then(res => {
      chapter.value = res.data
      fetchSubjectName(res.data.subject_id)
    })
    .catch(err => {
      console.error("❌ Failed to fetch chapter", err)
    })
}

function fetchSubjectName(subjectId) {
  axios.get(`/api/admin/subjects/${subjectId}`)
    .then(res => {
      subjectName.value = res.data.name
    })
    .catch(err => {
      console.error("❌ Failed to fetch subject", err)
    })
}

function fetchQuizzes() {
  axios.get(`/api/admin/chapters/${chapterId}/quizzes`).then(res => {
    quizzes.value = res.data
    filteredQuizzes.value = res.data
  })
}

function openQuizForm(quiz = null) {
  editingQuiz.value = quiz
  showQuizForm.value = true
}

function deleteQuiz(id) {
  axios.delete(`/api/admin/quizzes/${id}`).then(fetchQuizzes)
}

function openChapterForm(chap = null) {
  editingChapter.value = chap
  showChapterForm.value = true
}

function deleteChapter() {
  axios.delete(`/api/admin/chapters/${chapterId}`).then(() => {
    router.push(`/admin/subjects/${chapter.value.subject_id}`)
  })
}

function viewQuiz(quiz) {
  router.push(`/admin/quizzes/${quiz.id}/details`)
}

onMounted(() => {
  fetchChapter()
  fetchQuizzes()

  // 🌐 Global search support for quizzes
  window.addEventListener('admin-search', (e) => {
    const term = e.detail.value.toLowerCase()
    filteredQuizzes.value = quizzes.value.filter(quiz =>
      quiz.name?.toLowerCase().includes(term) ||
      quiz.deadline?.toLowerCase().includes(term)
    )
  })
})
</script>

<style scoped>
.initials-box {
  width: 100px;
  height: 100px;
  background-color: #14518f;
  color: white;
  font-size: 2.2rem;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}
.cursor-pointer {
  cursor: pointer;
}

.table  th{
  font-weight: bold
}
</style>
