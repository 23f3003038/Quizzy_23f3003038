<template>
  <div class="container py-4">
    <!-- Back Button -->
    <div class="mb-3 d-flex align-items-center cursor-pointer" @click="goBack">
      <i class="bi bi-arrow-left me-2"></i> Back
    </div>

    <!-- Breadcrumb -->
    <div class="text-muted mb-3">
      Subject / {{ subjectName }} / {{ chapterName }} / <strong>{{ quiz?.name }}</strong>
    </div>

    <!-- Quiz Info Box -->
    <div class="d-flex align-items-start gap-3 mb-4 p-3 border rounded shadow-sm">
      <!-- Serial No. Box -->
      <div class="initials-box">{{ quizCode }}</div>

      <!-- Info -->
      <div class="flex-grow-1">
        <h4 class="mb-1">{{ quiz?.name }}</h4>
        <p class="text-muted">{{ quiz?.description }}</p>

        <div class="d-flex gap-2 mt-2">
          <button class="btn btn-sm btn-secondary" @click="openQuizForm(quiz)">Edit</button>
          <button class="btn btn-sm btn-danger" @click="deleteQuiz">Delete</button>
        </div>
      </div>
    </div>

    <!-- + Add Question -->
    <div class="mb-3 text-end">
      <button class="btn btn-primary" @click="openQuestionForm()">+ Add Question</button>
    </div>

    <!-- Questions Table -->
    <h5 class="mb-3">Questions</h5>
    <div class="table-responsive">
      <table class="table table-hover">
        <thead>
          <tr>
            <th>S.No</th>
            <th>Question</th>
            <th>Correct Answer</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredQuestions.length === 0">
            <td colspan="4" class="text-center text-muted py-4">
              No results found.
            </td>
          </tr>
          <tr v-for="(question, index) in filteredQuestions" :key="question.id">
            <td>{{ index + 1 }}</td>
            <td>{{ question.question_statement }}</td>
            <td>{{ question['option' + question.correct_option] }}</td>
            <td>
              <button class="btn btn-sm btn-outline-secondary me-1" @click="openQuestionForm(question)">Edit</button>
              <button class="btn btn-sm btn-outline-danger" @click="deleteQuestion(question.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Question Form -->
    <QuestionForm
      v-if="showQuestionForm"
      :key="editingQuestion?.id || 'new'"
      :quiz-id="Number(quizId)"
      :question="editingQuestion"
      @saved="fetchQuestions"
      @close="showQuestionForm = false"
    />

    <!-- Quiz Form Modal -->
    <QuizForm
      v-if="showQuizForm"
      :quiz="editingQuiz"
      :chapter-id="quiz?.chapter_id"
      @saved="fetchQuiz"
      @close="showQuizForm = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import QuestionForm from './question-form.vue'
import QuizForm from './quiz-form.vue'

const route = useRoute()
const router = useRouter()

const quizId = route.params.id
const quiz = ref(null)
const questions = ref([])
const filteredQuestions = ref([])

const subjectName = ref('')
const chapterName = ref('')

const showQuestionForm = ref(false)
const editingQuestion = ref(null)

const showQuizForm = ref(false)
const editingQuiz = ref(null)

const quizCode = computed(() => {
  return quiz.value?.id ? `QZ${quiz.value.id.toString().padStart(2, '0')}` : ''
})

function goBack() {
  router.back()
}

function fetchQuiz() {
  axios.get(`/api/admin/quizzes/${quizId}`).then(res => {
    quiz.value = res.data
    fetchChapter(res.data.chapter_id)
  })
}

function fetchChapter(chapterId) {
  axios.get(`/api/admin/chapters/${chapterId}`).then(res => {
    chapterName.value = res.data.name
    fetchSubject(res.data.subject_id)
  })
}

function fetchSubject(subjectId) {
  axios.get(`/api/admin/subjects/${subjectId}`).then(res => {
    subjectName.value = res.data.name
  })
}

function fetchQuestions() {
  axios.get(`/api/admin/quizzes/${quizId}/questions`).then(res => {
    questions.value = res.data
    filteredQuestions.value = res.data
  })
}

function openQuestionForm(q = null) {
  editingQuestion.value = q
  showQuestionForm.value = true
}

function openQuizForm(q = null) {
  editingQuiz.value = q
  showQuizForm.value = true
}

function deleteQuestion(id) {
  axios.delete(`/api/admin/questions/${id}`).then(fetchQuestions)
}

function deleteQuiz() {
  axios.delete(`/api/admin/quizzes/${quizId}`).then(() => {
    router.back()
  })
}

onMounted(() => {
  fetchQuiz()
  fetchQuestions()

  // Global search listener - now only filters by question and correct answer
  window.addEventListener('admin-search', (e) => {
    const term = e.detail.value.toLowerCase()
    filteredQuestions.value = questions.value.filter(q => {
      const correctAnswer = q['option' + q.correct_option]?.toLowerCase() || ''
      return (
        q.question_statement?.toLowerCase().includes(term) ||
        correctAnswer.includes(term)
      )
    })
  })
})
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.initials-box {
  width: 100px;
  height: 100px;
  background-color: #14518f;
  border-radius: 10px;
  font-weight: bold;
  font-size: 2.2rem;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
}

.table  th{
  font-weight: bold
}
</style>
