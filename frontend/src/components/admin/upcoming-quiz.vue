<!-- frontend/src/components/admin/upcoming-quiz.vue -->
<template>
  <div>
    <h2 class="mb-4">Upcoming Quizzes</h2>
    <div v-if="upcomingQuizzes.length > 0">
      <table class="table table-bordered table-striped">
        <thead>
          <tr>
            <th>#</th>
            <th>Quiz Title</th>
            <th>Subject</th>
            <th>Date & Time</th>
            <th>Duration</th>
            <th>Total Questions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(quiz, index) in upcomingQuizzes" :key="quiz.id">
            <td>{{ index + 1 }}</td>
            <td>{{ quiz.name }}</td>
            <td>{{ quiz.subject?.name || '—' }}</td>
            <td>{{ formatDateTime(quiz.date_of_quiz) }}</td>
            <td>{{ quiz.duration }} mins</td>
            <td>{{ quiz.total_questions }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else>
      <p>No upcoming quizzes scheduled.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const upcomingQuizzes = ref([])

onMounted(async () => {
  try {
    const res = await axios.get('/api/admin/quizzes')
    const allQuizzes = res.data || []

    const now = new Date()

    upcomingQuizzes.value = allQuizzes.filter(q => {
      const quizDate = new Date(q.date_of_quiz)
      return quizDate > now
    })
  } catch (err) {
    console.error('Failed to fetch quizzes:', err)
  }
})

function formatDateTime(dateString) {
  const d = new Date(dateString)
  return isNaN(d.getTime()) ? 'Invalid Date' : d.toLocaleString()
}
</script>
