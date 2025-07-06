<template>
  <div class="modal-backdrop">
    <div class="modal-dialog">
      <div class="modal-content p-3">
        <h5>{{ question?.id ? 'Edit' : 'New' }} Question</h5>

        <textarea
          v-model="form.question_statement"
          class="form-control my-2"
          placeholder="Question statement"
        />

        <div
          v-for="(option, index) in form.options"
          :key="index"
          class="input-group my-2"
        >
          <input
            v-model="form.options[index]"
            class="form-control"
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

        <button
          class="btn btn-sm btn-outline-primary mb-2"
          @click="addOption"
          v-if="form.options.length < 4"
        >
          + Add Option
        </button>

        <select
          v-model.number="form.correct_option"
          class="form-select my-2"
        >
          <option disabled value="">Select correct option</option>
          <option v-for="(opt, i) in form.options" :key="i" :value="i + 1">
            Option {{ i + 1 }}
          </option>
        </select>

        <div class="d-flex gap-2 mt-3">
          <button class="btn btn-success" @click="save">Save</button>
          <button class="btn btn-outline-secondary" @click="$emit('close')">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
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

// Watch for prop changes (or mount) and initialize form accordingly
watch(
  () => props.question,
  (q) => {
    if (q) {
      form.question_statement = q.question_statement || ''
      form.options = []

      for (let i = 1; i <= 4; i++) {
        const key = `option${i}`
        if (q[key]) form.options.push(q[key])
      }

      // Ensure minimum 2 options
      while (form.options.length < 2) {
        form.options.push('')
      }

      form.correct_option = q.correct_option || 1
    } else {
      // Reset for new question
      form.question_statement = ''
      form.options = ['', '']
      form.correct_option = 1
    }
  },
  { immediate: true }
)

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
}

function save() {
  if (!form.question_statement.trim()) {
    alert('Question cannot be empty.')
    return
  }

  const filledOptions = form.options.filter(opt => opt.trim())
  if (filledOptions.length < 2) {
    alert('At least two options are required.')
    return
  }

  if (form.correct_option < 1 || form.correct_option > form.options.length) {
    alert('Select a valid correct option.')
    return
  }

  // Construct payload with options as option1, option2, ...
  const payload = {
    question_statement: form.question_statement,
    correct_option: form.correct_option
  }
  form.options.forEach((opt, index) => {
    payload[`option${index + 1}`] = opt
  })

  const req = props.question?.id
    ? axios.put(`/api/admin/questions/${props.question.id}`, payload)
    : axios.post(`/api/admin/quizzes/${props.quizId}/questions`, payload)

  req.then(() => {
    emit('saved')
    emit('close')
  }).catch(err => {
    alert('Error saving question.')
    console.error(err)
  })
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-dialog {
  width: 100%;
  max-width: 600px;
  background: white;
}
</style>
