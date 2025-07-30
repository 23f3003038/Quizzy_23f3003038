<template>
  <div class="modal-backdrop">
    <div class="modal-dialog">
      <div class="modal-content p-3">
        <h5>{{ question?.id ? 'Edit' : 'New' }} Question</h5>

        <!-- Question Statement -->
        <div class="mb-2">
          <textarea
            v-model="form.question_statement"
            @blur="validateField('question_statement')"
            @input="validateField('question_statement')"
            class="form-control"
            placeholder="Question statement"
            :class="{ 'is-invalid': errors.question_statement }"
          />
          <div v-if="errors.question_statement" class="invalid-feedback">
            {{ errors.question_statement }}
          </div>
        </div>

        <!-- Options -->
        <div
          v-for="(option, index) in form.options"
          :key="index"
          class="input-group mb-2"
        >
          <input
            v-model="form.options[index]"
            @input="validateField('options')"
            :class="{ 'form-control': true, 'is-invalid': errors.options }"
            :placeholder="`Option ${index + 1}`"
          />
          <button
            class="btn btn-outline-danger"
            v-if="form.options.length > 2"
            @click="removeOption(index)"
            title="Remove this option"
          >
            ×
          </button>
        </div>
        <div v-if="errors.options" class="invalid-feedback d-block mb-2">
          {{ errors.options }}
        </div>

        <button
          class="btn btn-sm btn-outline-primary mb-3"
          @click="addOption"
          v-if="form.options.length < 4"
        >
          + Add Option
        </button>

        <!-- Correct Option -->
        <div class="mb-3">
          <select
            v-model.number="form.correct_option"
            @change="validateField('correct_option')"
            :class="{ 'form-select': true, 'is-invalid': errors.correct_option }"
          >
            <option disabled value="">Select correct option</option>
            <option v-for="(_, i) in form.options" :key="i" :value="i + 1">
              Option {{ i + 1 }}
            </option>
          </select>
          <div v-if="errors.correct_option" class="invalid-feedback">
            {{ errors.correct_option }}
          </div>
        </div>

        <!-- Actions -->
        <div class="d-flex gap-2 mt-3">
          <button
            class="btn btn-success"
            @click="save"
            :disabled="!isFormValid || saving"
          >
            Save
          </button>
          <button
            class="btn btn-outline-secondary"
            @click="$emit('close')"
          >
            Cancel
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
      role="alert"
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

const props = defineProps({
  question: Object,
  quizId: Number
})
const emit = defineEmits(['saved', 'close'])

const form = reactive({
  question_statement: '',
  options: ['', ''],
  correct_option: 1
})

// validation errors
const errors = reactive({
  question_statement: '',
  options: '',
  correct_option: ''
})
const saving = ref(false)

// overall form validity
const isFormValid = computed(() => (
  form.question_statement.trim() !== '' &&
  form.options.filter(o => o.trim()).length >= 2 &&
  form.correct_option >= 1 &&
  form.correct_option <= form.options.length &&
  !errors.question_statement &&
  !errors.options &&
  !errors.correct_option
))

// initialize or reset form when editing vs. creating
watch(() => props.question, q => {
  if (q) {
    form.question_statement = q.question_statement || ''
    form.options = []
    for (let i = 1; i <= 4; i++) {
      const key = `option${i}`
      if (q[key]) form.options.push(q[key])
    }
    while (form.options.length < 2) {
      form.options.push('')
    }
    form.correct_option = q.correct_option || 1
  } else {
    form.question_statement = ''
    form.options = ['', '']
    form.correct_option = 1
  }
  // clear previous errors
  errors.question_statement = ''
  errors.options = ''
  errors.correct_option = ''
}, { immediate: true })

// field‐specific validation
function validateField(field) {
  switch (field) {
    case 'question_statement':
      errors.question_statement = form.question_statement.trim()
        ? ''
        : 'Question cannot be empty.'
      break
    case 'options':
      const count = form.options.filter(o => o.trim()).length
      errors.options = count >= 2
        ? ''
        : 'At least two options are required.'
      break
    case 'correct_option':
      errors.correct_option = (
        form.correct_option >= 1 &&
        form.correct_option <= form.options.length
      ) ? '' : 'Select a valid correct option.'
      break
  }
}

function addOption() {
  if (form.options.length < 4) {
    form.options.push('')
  }
}

function removeOption(index) {
  if (form.options.length > 2) {
    form.options.splice(index, 1)
    if (form.correct_option > form.options.length) {
      form.correct_option = form.options.length
    }
  }
  validateField('options')
}

// toast state
const showToast    = ref(false)
const toastMessage = ref('')
const toastType    = ref('success')
function showToastMessage(msg, type = 'success') {
  toastMessage.value = msg
  toastType.value    = type
  showToast.value    = true
  setTimeout(() => showToast.value = false, 1500)
}

async function save() {
  // run all validators
  validateField('question_statement')
  validateField('options')
  validateField('correct_option')
  if (!isFormValid.value) return

  saving.value = true

  // build payload
  const payload = {
    question_statement: form.question_statement,
    correct_option: form.correct_option
  }
  form.options.forEach((opt, idx) => {
    payload[`option${idx+1}`] = opt
  })

  try {
    const req = props.question?.id
      ? axios.put(`/api/admin/questions/${props.question.id}`, payload)
      : axios.post(`/api/admin/quizzes/${props.quizId}/questions`, payload)
    await req

    showToastMessage(
      props.question?.id
        ? '✅ Question updated successfully!'
        : '✅ Question saved successfully!'
    )

    setTimeout(() => {
      emit('saved')
      emit('close')
    }, 1500)
  } catch (err) {
    showToastMessage('❌ Error saving question.', 'error')
    console.error(err)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  background: rgba(0,0,0,0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050;
}
.modal-dialog {
  background: #fff;
  padding: 1rem;
  border-radius: 0.5rem;
  max-width: 600px;
  width: 100%;
}
.toast-container {
  z-index: 1100;
}
</style>
