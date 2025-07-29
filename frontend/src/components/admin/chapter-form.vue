<template>
  <div class="modal-backdrop-custom">
    <div class="modal-container">
      <div class="modal-card">
        <!-- Header -->
        <div class="modal-header d-flex justify-content-between align-items-center mb-3">
          {{ props.subjectName || '...' }} / <strong>{{ chapter?.id ? 'EDIT CHAPTER' : 'ADD CHAPTER' }}</strong>
          <button class="btn-close" @click="$emit('close')" title="Close (ESC)"></button>
        </div>

        <!-- Form Inputs -->
         <div>
          <input
            v-model="form.name"
            @blur="validateField('name')"      
            @input="validateField('name')" 
            class="form-control mb-2"
            placeholder="Chapter Name"
            :class="{ 'is-invalid': errors.name }"
          />
          <div v-if="errors.name" class="invalid-feedback">
              {{ errors.name }}
          </div>
        </div>
        <div>
          <textarea
            v-model="form.description"
            @blur="validateField('description')"  
            @input="validateField('description')" 
            class="form-control"
            placeholder="Add description..."
            :class="{ 'is-invalid': errors.description }"
          ></textarea>
          <div v-if="errors.description" class="invalid-feedback">
            {{ errors.description }}
          </div>
        </div>

        <!-- Buttons -->
        <div class="d-flex justify-content-end gap-2">
          <button class="btn btn-outline-secondary" @click="$emit('close')">Cancel</button>
          <button class="btn btn-dark" @click="save" :disabled="!isFormValid || saving" >
            {{ props.chapter?.id ? 'Update' : 'Create' }} Chapter
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Toast -->
  <div class="toast-container position-fixed top-0 end-0 p-3" style="z-index: 1100">
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
import { reactive, ref, watch, computed } from 'vue'
import axios from 'axios'

const props = defineProps({ chapter: Object, subjectId: Number, subjectName: String })
const emit = defineEmits(['saved', 'close'])

const form = reactive({ name: '', description: '' })

// Validation state
const errors = reactive({                                               // ⬅️ Added
  name: '',
  description: ''
})
const saving = ref(false)                                               // ⬅️ Added

// Initialize form on edit
watch(
  () => props.chapter,
  (c) => {
    form.name        = c?.name || ''
    form.description = c?.description || ''
    // clear errors
    errors.name = ''
    errors.description = ''
  },
  { immediate: true }
)

// Field validator
function validateField(field) {                                         // ⬅️ Added
  if (field === 'name') {
    errors.name = form.name.trim() ? '' : 'Chapter name is required'
  }
  if (field === 'description') {
    errors.description = form.description.trim()
      ? ''
      : 'Description is required'
  }
}

// Overall form validity
const isFormValid = computed(() =>                                      // ⬅️ Added
  form.name.trim() !== '' &&
  form.description.trim() !== ''
)

const showToast = ref(false)
const toastMessage = ref('')
const toastType = ref('success')

function showToastMessage(message, type = 'success') {
  toastMessage.value = message
  toastType.value = type
  showToast.value = true
  setTimeout(() => (showToast.value = false), 1500)
}

function save() {
  validateField('name')                                            
  validateField('description')                                      

  if (!isFormValid.value) return                                      

  saving.value = true 
  const payload = { name: form.name, description: form.description }

  const req = props.chapter?.id
    ? axios.put(`/api/admin/chapters/${props.chapter.id}`, payload)
    : axios.post(`/api/admin/subjects/${props.subjectId}/chapters`, payload)

  req
    .then(() => {
      showToastMessage('✅ Chapter created!', 'success')
      setTimeout(() => {
        emit('saved')
        emit('close')
        form.name = ''
        form.description = ''
      }, 1500)
    })
    .catch(() => {
      showToastMessage('❌ Failed to save chapter.', 'error')
    })
    .finally(() => (saving.value = false))
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
</style>
