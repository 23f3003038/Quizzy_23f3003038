<template>
  <div class="quiz-attempt container py-4">
    <!-- Toast Notifications -->
    <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 2000;">
      <div
        class="toast align-items-center text-white border-0 mb-2"
        :class="{
          'bg-success': toastType === 'success',
          'bg-danger': toastType === 'error',
          show: showToast
        }"
        role="alert"
        aria-live="assertive"
        aria-atomic="true"
      >
        <div class="d-flex">
          <div class="toast-body">
            {{ toastMessage }}
          </div>
          <button
            type="button"
            class="btn-close btn-close-white me-2 m-auto"
            @click="showToast = false"
          ></button>
        </div>
      </div>
    </div>

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

// Toast state
const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

function showToastMessage(msg, type = 'success') {
  toastMessage.value = msg
  toastType.value = type
  showToast.value = true
  setTimeout(() => { showToast.value = false }, 3000)
}


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
  axios.get(`/api/user/quizzes/${quizId}`)
    .then(res => {
      questions.value = res.data.questions.map(q => {
        const options = [q.option1, q.option2, q.option3, q.option4].filter(Boolean)
        return { ...q, options }
      })

      durationInSeconds.value = parseDuration(res.data.duration)
      timeLeft.value = durationInSeconds.value

      startTimer()
    })
    .catch(err => {
      console.error('❌ Error fetching quiz data:', err)
      showToastMessage('Failed to load quiz.', 'error')
      setTimeout(() => router.push('/user/dashboard'), 1500)
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
      showToastMessage('⚠️ Only 5 minutes remaining!', 'error')
    }

    if (timeLeft.value <= 0) {
      clearInterval(timerInterval.value)
      submitQuiz(true)
    }
  }, 2500)
}

async function submitQuiz(auto = false) {
  clearInterval(timerInterval.value)
  window.removeEventListener('beforeunload', confirmExit)

  const payload = {
    answers: Object.entries(answers.value).map(([question_id, selected]) => ({
      question_id: parseInt(question_id),
      selected
    }))
  }

  try {
    const { data } = await axios.post(
      `/api/user/quizzes/${quizId}/submit`,
      payload
    )
    if (auto) {
      showToastMessage("⏰ Time's up! Your quiz was auto-submitted.", 'error')
    }
    // redirect to the result page for this exact attempt
    router.push({
      name: 'UserQuizResult',
      params: { attemptId: data.id }
    })
  } catch (err) {
    console.error('❌ Submission failed:', err)
    showToastMessage('Failed to submit quiz.', 'error')
  }
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
  margin-left: 1.2rem;
}

.form-check-label {
  display: inline-block;
  margin-left: 0.5rem;
  line-height: 1.4;
  white-space: normal;
  width: 100%;
}

/* Toast overrides */
.toast {
  opacity: 1;
  transition: opacity 0.3s ease;
}
.toast.show {
  opacity: 1;
}
</style>
