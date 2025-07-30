<template>
  <div class="modal-backdrop-custom">
    <div class="modal-container">
      <div class="modal-card">
        <!-- Header -->
        <div class="modal-header d-flex justify-content-between align-items-center mb-3">
          <small class="text-muted">
            ADMIN / <strong>{{ quiz?.id ? 'EDIT QUIZ' : 'CREATE QUIZ' }}</strong>
          </small>
          <button class="btn-close" @click="$emit('close')" title="Close (ESC)"></button>
        </div>

        <!-- Form Inputs -->
        <div class="mb-3">
          <input
            v-model="form.name"
            @blur="validateField('name')"
            @input="validateField('name')"
            class="form-control"
            placeholder="Quiz Name"
            :class="{ 'is-invalid': errors.name }"
          />
          <div v-if="errors.name" class="invalid-feedback">
            {{ errors.name }}
          </div>
        </div>

        <div class="mb-3">
          <textarea
            v-model="form.description"
            class="form-control"
            placeholder="Add Description..."
          ></textarea>
        </div>

        <div class="mb-3">
          <input
            v-model="form.duration"
            @blur="validateField('duration')"
            @input="validateField('duration')"
            type="text"
            placeholder="Time Duration (HH:MM)"
            class="form-control"
            :class="{ 'is-invalid': errors.duration }"
          />
          <div v-if="errors.duration" class="invalid-feedback">
            {{ errors.duration }}
          </div>
        </div>

        <div class="mb-4">
          <input
            v-model="form.deadline"
            @change="validateField('deadline')"
            type="date"
            class="form-control"
            :class="{ 'is-invalid': errors.deadline }"
          />
          <div v-if="errors.deadline" class="invalid-feedback">
            {{ errors.deadline }}
          </div>
        </div>

        <textarea
          v-model="form.remarks"
          class="form-control mb-4"
          placeholder="Remarks (optional)"
        ></textarea>

        <div class="d-flex justify-content-end gap-2">
          <button class="btn btn-outline-secondary" @click="$emit('close')">
            Cancel
          </button>
          <button
            class="btn btn-dark"
            @click="save"
            :disabled="!isFormValid || saving"
          >
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
        <button
          type="button"
          class="btn-close btn-close-white me-2 m-auto"
          @click="showToast = false"
        ></button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, watch, computed } from 'vue'
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

const errors = reactive({
  name:     '',
  duration: '',
  deadline: ''
})
const saving = ref(false)

// form is valid if all required fields are filled and no errors
const isFormValid = computed(() => (
  form.name.trim() !== '' &&
  !errors.name &&
  form.duration.trim() !== '' &&
  !errors.duration &&
  form.deadline !== '' &&
  !errors.deadline
))

// When `quiz` prop changes (or on mount), populate form.
// Note: we slice the ISO datetime to YYYY-MM-DD for the <input type="date">
watch(() => props.quiz, q => {
  form.name        = q?.name         || ''
  form.description = q?.description  || ''
  form.duration    = q?.duration     || ''
  form.deadline    = q?.deadline
    ? q.deadline.slice(0, 10)
    : ''
  form.remarks     = q?.remarks      || ''

  // clear any old errors
  errors.name     = ''
  errors.duration = ''
  errors.deadline = ''
}, { immediate: true })

// per-field validator
function validateField(field) {
  switch (field) {
    case 'name':
      errors.name = form.name.trim()
        ? ''
        : 'Quiz name is required.'
      break

    case 'duration':
      errors.duration = form.duration.trim()
        ? ''
        : 'Duration is required.'
      break

    case 'deadline':
      if (!form.deadline) {
        errors.deadline = 'Deadline is required.'
      } else if (new Date(form.deadline) < new Date(new Date().toDateString())) {
        errors.deadline = 'Deadline cannot be in the past.'
      } else {
        errors.deadline = ''
      }
      break
  }
}

const showToast    = ref(false)
const toastMessage = ref('')
const toastType    = ref('success')
function showToastMessage(msg, type = 'success') {
  toastMessage.value = msg
  toastType.value    = type
  showToast.value    = true
  setTimeout(() => (showToast.value = false), 1500)
}

async function save() {
  // run all validators
  validateField('name')
  validateField('duration')
  validateField('deadline')
  if (!isFormValid.value) return

  saving.value = true
  const payload = {
    name:        form.name,
    description: form.description,
    duration:    form.duration,
    deadline:    form.deadline,
    remarks:     form.remarks
  }

  try {
    const req = props.quiz?.id
      ? axios.put(`/api/admin/quizzes/${props.quiz.id}`, payload)
      : axios.post(`/api/admin/chapters/${props.chapterId}/quizzes`, payload)
    await req

    showToastMessage(
      props.quiz?.id
        ? '✅ Quiz updated successfully!'
        : '✅ Quiz created successfully!'
    )
    setTimeout(() => {
      emit('saved')
      emit('close')
    }, 1500)
  } catch {
    showToastMessage('❌ Failed to save quiz.', 'error')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.modal-backdrop-custom {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  backdrop-filter: blur(1.5px);
  background-color: rgba(0,0,0,0.2);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}
.modal-container {
  max-width: 500px; width: 100%; padding: 1rem;
}
.modal-card {
  background: #fff;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}
.toast-container { z-index: 1055; }
</style>
