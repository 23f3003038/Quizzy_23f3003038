<template>
  <div class="modal-backdrop-custom">
    <div class="modal-container">
      <div class="modal-card">
        <!-- Header -->
        <div class="modal-header d-flex justify-content-between align-items-center mb-3">
          <small class="text-muted">ADMIN / <strong>{{ quiz?.id ? 'EDIT QUIZ' : 'CREATE QUIZ' }}</strong></small>
          <button class="btn-close" @click="$emit('close')" title="Close (ESC)"></button>
        </div>

        <!-- Form Inputs -->
        <input
          v-model="form.name"
          class="form-control mb-2"
          placeholder="Quiz Name"
        />
        <textarea
          v-model="form.description"
          class="form-control mb-2"
          placeholder="Add Description..."
        ></textarea>
        <input
          v-model="form.duration"
          type="text"
          placeholder="Time Duration (HH:MM)"
          class="form-control mb-2"
        />
        <input
          v-model="form.deadline"
          type="date"
          class="form-control mb-4"
        />
        <textarea
          v-model="form.remarks"
          class="form-control mb-4"
          placeholder="Remarks (optional)"
        ></textarea>

        <!-- Buttons -->
        <div class="d-flex justify-content-end gap-2">
          <button class="btn btn-outline-secondary" @click="$emit('close')">Cancel</button>
          <button class="btn btn-dark" @click="save">
            {{ quiz?.id ? 'Update' : 'Create' }} Quiz
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Toast -->
  <div class="toast-container position-fixed top-0 end-0 p-3">
    <div
      class="toast align-items-center text-white"
      :class="{
        'bg-success': toastType === 'success',
        'bg-danger': toastType === 'error',
        show: showToast
      }"
    >
      <div class="d-flex">
        <div class="toast-body">{{ toastMessage }}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" @click="showToast = false"></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import axios from 'axios'

const props = defineProps({ quiz: Object, chapterId: Number })
const emit = defineEmits(['saved', 'close'])

const form = reactive({
  name: '',
  description: '',
  duration: '',
  deadline: '',
  remarks: ''
})

const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

watch(
  () => props.quiz,
  (q) => {
    form.name = q?.name || ''
    form.description = q?.description || ''
    form.duration = q?.duration || ''
    form.deadline = q?.deadline || ''
    form.remarks = q?.remarks || ''
  },
  { immediate: true }
)

function showToastMessage(message, type = 'success') {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  setTimeout(() => (showToast.value = false), 1500)
}

function save() {
  const payload = {
    name: form.name,
    description: form.description,
    duration: form.duration,
    deadline: form.deadline,
    remarks: form.remarks
  }

  console.log("📤 Sending quiz update payload:", payload)

  const req = props.quiz?.id
    ? axios.put(`/api/admin/quizzes/${props.quiz.id}`, payload)
    : axios.post(`/api/admin/chapters/${props.chapterId}/quizzes`, payload)

  req
    .then(() => {
      showToastMessage('✅ Quiz saved successfully!', 'success')
      setTimeout(() => {
        emit('saved')
        emit('close')
      }, 1500)
    })
    .catch(() => {
      showToastMessage('❌ Failed to save quiz.', 'error')
    })
}
</script>

<style scoped>
.modal-backdrop-custom {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  backdrop-filter: blur(1.5px);
  background-color: rgba(0, 0, 0, 0.2);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}

.modal-container {
  max-width: 500px;
  width: 100%;
  padding: 1rem;
}

.modal-card {
  background: #fff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
  position: relative;
}

.toast-container {
  z-index: 1055;
}
</style>
