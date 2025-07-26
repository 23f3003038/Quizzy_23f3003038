<template>
  <div>
    <h3>Questions</h3>
    <button class="btn btn-primary mb-2" @click="openForm()">+ New Question</button>
    <table class="table">
      <thead>
        <tr>
          <th>Statement</th>
          <th>Option 1</th>
          <th>Option 2</th>
          <th>Option 3</th>
          <th>Option 4</th>
          <th>Correct</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="q in filteredQuestions" :key="q.id">
          <td>{{ q.question_statement }}</td>
          <td>{{ q.option1 }}</td>
          <td>{{ q.option2 }}</td>
          <td>{{ q.option3 }}</td>
          <td>{{ q.option4 }}</td>
          <td>{{ q.correct_option }}</td>
          <td>
            <button class="btn btn-sm btn-secondary" @click="openForm(q)">Edit</button>
            <button class="btn btn-sm btn-danger" @click="remove(q.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <QuestionForm
      v-if="showForm"
      :question="current"
      :quizId="quizId"
      @saved="fetch()"
      @close="showForm = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import QuestionForm from './question-form.vue'

const props = defineProps({
  quizId: Number
})

const questions = ref([])
const filteredQuestions = ref([])

const showForm = ref(false)
const current = ref(null)

function fetch() {
  axios.get(`/api/admin/quizzes/${props.quizId}/questions`)
    .then(res => {
      questions.value = res.data
      filteredQuestions.value = res.data
    })
}

function openForm(q = null) {
  current.value = q
  showForm.value = true
}

function remove(id) {
  axios.delete(`/api/admin/questions/${id}`)
    .then(fetch)
}

onMounted(() => {
  fetch()

  window.addEventListener('admin-search', (e) => {
    const term = e.detail.value.toLowerCase()
    filteredQuestions.value = questions.value.filter(q =>
      q.question_statement?.toLowerCase().includes(term) ||
      q.option1?.toLowerCase().includes(term) ||
      q.option2?.toLowerCase().includes(term) ||
      q.option3?.toLowerCase().includes(term) ||
      q.option4?.toLowerCase().includes(term)
    )
  })
})
</script>
