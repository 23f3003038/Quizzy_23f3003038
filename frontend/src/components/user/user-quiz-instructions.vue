<template>
  <div class="modal-backdrop-custom" @click.self="onClose">
    <div class="modal-container">
      <div class="modal-card">
        <!-- Close Button -->
        <button class="btn-close position-absolute top-2 end-2" @click="onClose" title="Close">
          &times;
        </button>

        <!-- Back Button -->
        <div class="mb-3 text-primary cursor-pointer fw-medium" @click="onClose">
          <i class="bi bi-arrow-left" style="color:#337665"></i> Back
        </div>

        <!-- Quiz Title -->
        <h3 class="fw-bold mb-3">{{ quiz.name }}</h3>

        <!-- Quiz Info -->
        <p><strong>Duration:</strong> {{ formatDuration(quiz.duration) }}</p>
        <p><strong>Total Questions:</strong> {{ quiz.questions?.length || 0 }}</p>

        <!-- Rules -->
        <div class="quiz">
          <p><b>Are u ready to start the quiz? Once started:</b></p>
          <h5>Instructions</h5>
          <ul>
            <li>Each question has only one correct answer.</li>
            <li>There is no negative marking.</li>
            <li>You can review your answers before final submission</li>
            <li>Timer starts once you begin.</li>
            <li>Make sure u have a stable internet connection.</li>
          </ul>
        </div>

        <!-- Availability Message -->
        <div v-if="!isAvailable" class="alert alert-warning mt-3">
          ⏳ This quiz can only be attempted before <strong>{{ formatDate(quiz.deadline) }}</strong>.
        </div>

        <!-- Action Buttons -->
        <div class="d-flex justify-content-end mt-4 gap-2">
          <button class="btn btn-outline-secondary" @click="onClose">
            Cancel
          </button>
          <button class="btn btn-dark" @click="startQuiz" :disabled="!isAvailable">
            Start Now
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({ quiz: Object })
const emit = defineEmits(['close'])
const router = useRouter()

// Emit close event to parent
function onClose() {
  emit('close')
}

// Close modal and navigate to quiz attempt
function startQuiz() {
  emit('close')
  router.push(`/user/quiz/${props.quiz.id}/attempt/live`)
}

// Compute availability
const isAvailable = computed(() => {
  if (!props.quiz.date_of_quiz || !props.quiz.deadline) return false
  const now = new Date()
  const start = new Date(props.quiz.date_of_quiz)
  const end = new Date(props.quiz.deadline)
  return now >= start && now <= end
})

// Formatting helpers
function formatDuration(durationStr) {
  if (!durationStr || durationStr === 'None') return 'N/A'
  const [h, m] = durationStr.split(':')
  return `${parseInt(h)}h ${parseInt(m)}m`
}

function formatDate(utc) {
  if (!utc) return 'N/A'
  // Parse date and format date part only, then append midnight
  const dateObj = new Date(utc)
  const datePart = dateObj.toLocaleDateString('en-IN', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
  return `${datePart}, 12:00 am`
}
</script>

<style scoped>
.modal-backdrop-custom {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  background-color: rgba(0, 0, 0, 0.2);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}
.modal-container {
  max-width: 600px;
  width: 100%;
  padding: 1rem;
}
.modal-card {
  position: relative;
  background: #fff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  max-height: 90vh;
  overflow-y: auto;
}
.btn-close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.quiz p {
  margin-top:-1.2rem;
  margin-bottom:0rem;
  font-size: 1rem;
}
</style>
