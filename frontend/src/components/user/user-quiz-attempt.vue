<template>
  <div class="quiz-attempt container py-4">
    <!-- Timer -->
    <div class="timer-bar alert alert-warning text-center fw-bold" role="alert">
      ⏳ Time Left: {{ formattedTime }}
    </div>

    <!-- Questions -->
    <div v-if="questions.length">
      <div
        v-for="(q, index) in questions"
        :key="q.id"
        class="mb-5 p-4 rounded shadow-sm border bg-white"
      >
        <!-- Question Statement -->
        <p class="fw-semibold mb-3">
          Q{{ index + 1 }}.
          <span v-html="formatQuestion(q.question_statement)"></span>
        </p>

        <!-- Options -->
        <div class="d-flex flex-column gap-2">
          <div
            v-for="(opt, i) in q.options"
            :key="i"
            class="form-check"
          >
            <input
              class="form-check-input"
              type="radio"
              :name="'question-' + q.id"
              :value="i + 1"
              v-model="answers[q.id]"
              :id="`q${q.id}_opt${i + 1}`"
            />
            <label class="form-check-label ms-2" :for="`q${q.id}_opt${i + 1}`">
              {{ opt }}
            </label>
          </div>
        </div>
      </div>

      <!-- Submit Button -->
      <div class="text-center">
        <button
          class="btn btn-success mt-4 px-5"
          :disabled="!allAnswered"
          @click="submitQuiz"
        >
          Submit Quiz
        </button>
      </div>
    </div>

    <div v-else class="text-center text-muted">Loading quiz...</div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const quizId = route.params.quizId
const questions = ref([])
const durationInSeconds = ref(0)
const timeLeft = ref(0)
const timerInterval = ref(null)

const answers = ref({})

// Format time in mm:ss
const formattedTime = computed(() => {
  const minutes = Math.floor(timeLeft.value / 60)
  const seconds = timeLeft.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

// All questions answered
const allAnswered = computed(() => {
  return questions.value.length > 0 &&
    questions.value.every(q => answers.value[q.id])
})

// Handle line breaks in question
function formatQuestion(statement) {
  return statement.replace(/\n/g, '<br>')
}

// Warn before navigating away
const confirmExit = (e) => {
  e.preventDefault()
  e.returnValue = ''
}

onMounted(() => {
  fetchQuizData()
  window.addEventListener('beforeunload', confirmExit)
})

onBeforeUnmount(() => {
  clearInterval(timerInterval.value)
  window.removeEventListener('beforeunload', confirmExit)
})

function fetchQuizData() {
  axios.get(`/api/user/quizzes/${quizId}`).then(res => {
    // console.log("Raw quiz question:", res.data.questions)

    questions.value = res.data.questions.map(q => {
      const options = [q.option1, q.option2, q.option3, q.option4].filter(Boolean)
      return { ...q, options }
    })

    durationInSeconds.value = parseDuration(res.data.duration)
    timeLeft.value = durationInSeconds.value

    startTimer()
  }).catch(err => {
    console.error("❌ Error fetching quiz data:", err?.response?.data || err.message || err)
    alert("Failed to load quiz.")
    router.push('/user/dashboard')
  })
}

function parseDuration(durationStr) {
  const [h, m, s] = durationStr.split(':').map(Number)
  return (h * 3600) + (m * 60) + (s || 0)
}

function startTimer() {
  timerInterval.value = setInterval(() => {
    timeLeft.value--

    if (timeLeft.value === 300) {
      alert('⚠️ Only 5 minutes remaining!')
    }

    if (timeLeft.value <= 0) {
      clearInterval(timerInterval.value)
      submitQuiz(true)
    }
  }, 1000)
}

function submitQuiz(auto = false) {
  clearInterval(timerInterval.value)
  window.removeEventListener('beforeunload', confirmExit)

  const payload = {
    answers: Object.entries(answers.value).map(([question_id, selected]) => ({
      question_id: parseInt(question_id),
      selected: selected
    }))
  }

  axios.post(`/api/user/quizzes/${quizId}/submit`, payload)
    .then(res => {
      // console.log("✅ Quiz submitted. Feedback:", res.data)

      if (auto) {
        alert("⏰ Time's up! Your quiz was auto-submitted.")
      }

      // If backend returns feedback or score, you can store it or pass it to results page.
      // For now we redirect:
      router.push(`/user/quiz/${quizId}/result`)
    })
    .catch(err => {
      console.error("❌ Submission failed:", err?.response?.data || err.message || err)
      alert("Failed to submit quiz.")
    })
}

</script>

<style scoped>
.quiz-attempt {
  max-width: 900px;
}

.timer-bar {
  font-size: 1.2rem;
}

.btn:disabled {
  opacity: 0.6;
  pointer-events: none;
}

.form-check {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 8px 0;
  border-bottom: 1px dashed #ccc;
  margin-left:1.2rem
}

.form-check-label {
  display: inline-block;
  margin-left: 0.5rem;
  line-height: 1.4;
  white-space: normal;
  width: 100%;
}
</style>
