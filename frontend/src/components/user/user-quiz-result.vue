<template>
  <div class="container py-4 quiz-result">
    <h2 class="mb-4 text-center">📊 Quiz Result</h2>

    <!-- Score Summary -->
    <div class="alert alert-info text-center fw-bold">
      You got {{ score.correct }} out of {{ score.total }} correct!
    </div>

    <!-- Questions Review -->
    <div
      v-for="(q, index) in questions"
      :key="q.question_id"
      class="mb-4 p-3 border rounded shadow-sm bg-white"
    >
      <p class="fw-semibold">
        Q{{ index + 1 }}. {{ q.question_statement }}
      </p>

      <!-- Options -->
      <div class="d-flex flex-column gap-2 mt-2">
        <div
          v-for="(opt, i) in q.options"
          :key="i"
          class="px-3 py-2 rounded"
          :class="optionClass(q, i + 1)"
        >
          <strong>{{ String.fromCharCode(65 + i) }}.</strong> {{ opt }}
          <span v-if="q.selected === i + 1" class="ms-2 badge bg-primary">Your Answer</span>
          <span v-if="q.correct_option === i + 1" class="ms-2 badge bg-success">Correct</span>
        </div>
      </div>

      <!-- Feedback (optional) -->
      <div v-if="q.is_correct !== undefined" class="mt-2 text-muted small">
        <template v-if="q.is_correct">
          ✅ You answered this question correctly.
        </template>
        <template v-else>
          ❌ The correct answer was option {{ q.correct_option }}.
        </template>
      </div>
    </div>

    <!-- Back Button -->
    <div class="text-center">
      <router-link class="btn btn-secondary mt-3" :to="{ name: 'user-dashboard' }">
        🔙 Back to Dashboard
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route     = useRoute()
const router    = useRouter()
// Use attemptId from route params
const attemptId = route.params.attemptId

const score     = ref({ correct: 0, total: 0 })
const questions = ref([])

onMounted(fetchResult)

function fetchResult() {
  axios.get(`/api/user/scores/${attemptId}/report`)
    .then(res => {
      const data = res.data
      score.value.correct = data.total_score
      score.value.total   = data.total_questions
      questions.value     = data.questions.map(q => ({
        question_id:      q.question_id,
        question_statement: q.question_statement,
        options:          q.options,
        selected:         q.selected,
        correct_option:   q.correct_option,
        is_correct:       q.is_correct
      }))
    })
    .catch(err => {
      console.error("❌ Failed to load result:", err)
      alert("Failed to load quiz result.")
      router.push({ name: 'user-dashboard' })
    })
}

function optionClass(q, optionNumber) {
  if (q.selected === optionNumber && q.correct_option !== optionNumber) {
    return 'bg-danger text-white border'
  }
  if (q.correct_option === optionNumber) {
    return 'bg-success text-white border'
  }
  return 'border'
}
</script>

<style scoped>
.quiz-result {
  max-width: 900px;
  margin: auto;
}

.badge {
  font-size: 0.75rem;
}

.bg-success {
  background-color: #28a745 !important;
}

.bg-danger {
  background-color: #dc3545 !important;
}

.bg-primary {
  background-color: #007bff !important;
}
</style>
