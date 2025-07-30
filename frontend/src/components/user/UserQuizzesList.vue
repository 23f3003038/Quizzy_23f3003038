<template>
  <div class="container py-4">
    <h2 class="mb-4">All Quizzes</h2>

    <div v-if="loading" class="text-center text-muted py-5">
      Loading quizzes…
    </div>
    <div v-else-if="!quizzes.length" class="text-center text-muted py-5">
      No quizzes available.
    </div>
    <div v-else class="list-group">
      <router-link
        v-for="quiz in quizzes"
        :key="quiz.id"
        :to="{ name: 'UserQuizDetails', params: { quizId: quiz.id } }"
        class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
      >
        <div>
          <strong># Quiz {{ quiz.id }} - {{ quiz.subject_name }}</strong>
          <div class="small text-muted">{{ quiz.chapter_name }}</div>
        </div>
        <small>{{ formatDate(quiz.date_of_quiz) }}</small>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const quizzes = ref([])
const loading = ref(true)

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-IN', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric', month: 'short', day: 'numeric'
  })
}

async function fetchQuizzes() {
  try {
    const res = await axios.get('/api/user/quizzes')
    const raw = Array.isArray(res.data) ? res.data : []

    // Enrich each quiz with chapter and subject names
    const enriched = await Promise.all(
      raw.map(async quiz => {
        try {
          const chapRes = await axios.get(`/api/user/chapters/${quiz.chapter_id}`)
          const chapter = chapRes.data
          const subjRes = await axios.get(`/api/user/subjects/${chapter.subject_id}`)
          const subject = subjRes.data
          return {
            ...quiz,
            chapter_name: chapter.name,
            subject_name: subject.name
          }
        } catch (err) {
          console.error('Failed to fetch chapter/subject for quiz', quiz.id, err)
          return {
            ...quiz,
            chapter_name: 'Unknown Chapter',
            subject_name: 'Unknown Subject'
          }
        }
      })
    )

    quizzes.value = enriched
  } catch (err) {
    console.error('❌ Failed to load quizzes:', err)
  } finally {
    loading.value = false
  }
}

onMounted(fetchQuizzes)
</script>

<style scoped>
.list-group-item {
  cursor: pointer;
}
</style>
