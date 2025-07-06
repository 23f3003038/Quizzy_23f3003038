<template>
  <div>
    <h3>Quizzes</h3>
    <button class="btn btn-primary mb-2" @click="openForm()">+ New Quiz</button>
    <table class="table">
      <thead><tr><th>Date</th><th>Duration</th><th>Remarks</th><th>Actions</th></tr></thead>
      <tbody>
        <tr  v-for="q in filteredQuizzes" :key="q.id">
          <td @click="goToQuestions(q)">{{ q.date_of_quiz }}</td>
          <td>{{ q.duration }}</td>
          <td>{{ q.remarks }}</td>
          <td>
            <button class="btn btn-sm btn-secondary" @click="openForm(q)">Edit</button>
            <button class="btn btn-sm btn-danger" @click="remove(q.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
    <QuizForm
      v-if="showForm"
      :quiz="current"
      :chapterId="id"
      @saved="fetch()"
      @close="showForm = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import QuizForm from './quiz-form.vue'

const props = defineProps({ id: Number })
const quizzes = ref([])
const filteredQuizzes = ref([])
const showForm = ref(false)
const current = ref(null)
const router = useRouter()

function fetch() {
  axios.get(`/api/admin/chapters/${props.id}/quizzes`).then(r => {
    quizzes.value = r.data
    filteredQuizzes.value = r.data
  })
}

function openForm(q = null) {
  current.value = q
  showForm.value = true
}

function remove(id) {
  axios.delete(`/api/admin/quizzes/${id}`).then(fetch)
}

function goToQuestions(q) {
  router.push(`/admin/quizzes/${q.id}/questions`)
}

onMounted(() => {
  fetch()

  window.addEventListener('admin-search', (e) => {
    const term = e.detail.value.toLowerCase()
    filteredQuizzes.value = quizzes.value.filter(quiz =>
      quiz.title?.toLowerCase().includes(term) ||
      quiz.description?.toLowerCase().includes(term)
    )
  })
})
</script>
