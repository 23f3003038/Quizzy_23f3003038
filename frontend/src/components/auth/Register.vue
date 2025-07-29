<template>
  <div class="registration-wrapper">
    <div class="card registration-card shadow-lg">
      <div class="row g-0">
        <!-- Form Column -->
        <div class="col-12 col-md-6 p-4">
          <h2 class="card-title text-center mb-4">Quizzy Registration</h2>
          <div v-if="serverError" class="alert alert-danger text-center">{{ serverError }}</div>
          <form @submit.prevent="register" novalidate>
            <div class="mb-3">
              <label class="form-label">Full Name</label>
              <input
                v-model="form.full_name"
                @blur="validateField('full_name')" 
                @input="validateField('full_name')"
                type="text"
                class="form-control"
                placeholder="Enter full name"
                :class="{ 'is-invalid': errors.full_name }"
              />
              <div v-if="errors.full_name" class="invalid-feedback">
                {{ errors.full_name }}
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input
                v-model="form.email"
                @blur="validateField('email')"
                @input="validateField('email')" 
                type="email"
                class="form-control"
                placeholder="abc@gmail.com"
                :class="{ 'is-invalid': errors.email }" 
              />
              <div v-if="errors.email" class="invalid-feedback">
                {{ errors.email }}
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input
                v-model="form.password"
                @blur="validateField('password')"
                @input="validateField('password')"
                type="password"
                class="form-control"
                placeholder="Enter password"
                :class="{ 'is-invalid': errors.password }"
              />
              <div v-if="errors.password" class="invalid-feedback">  <!-- ⬅️ Added -->
                {{ errors.password }}
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Qualification</label>
              <input
                v-model="form.qualification"
                type="text"
                class="form-control"
                placeholder="Enter your qualification (Optional)"
              />
            </div>
            <div class="mb-4">
              <label class="form-label">Date of Birth</label>
              <input
                v-model="form.dob"
                @change="validateField('dob')" 
                type="date"
                class="form-control"
                :class="{ 'is-invalid': errors.dob }"
              />
              <div v-if="errors.dob" class="invalid-feedback">
                {{ errors.dob }}
              </div>
            </div>
            <button type="submit" class="btn btn-primary w-100" :disabled="!isFormValid || registering">Register</button>
          </form>
          <p class="mt-3 text-center">
            Already have an account?
            <router-link to="/login" class="text-decoration-none">
              Login here
            </router-link>
          </p>
        </div>

        <!-- Image Column -->
        <div class="image col-12 col-md-6 d-none d-md-block">
          <img
            src="/Registration.png"
            alt="Quiz illustration"
            class="img-fluid h-100 w-100"
            style="object-fit: cover; border-radius: 0 2rem 2rem 0"
          />
        </div>
      </div>
    </div>

    <!-- ✅ Toast Notification -->
    <div
      class="toast-container position-fixed top-0 end-0 p-3"
      style="z-index: 1100"
    >
      <div
        class="toast align-items-center text-white bg-success border-0"
        role="alert"
        :class="{ show: showToast }"
        aria-live="assertive"
        aria-atomic="true"
      >
        <div class="d-flex">
          <div class="toast-body">
            Registration successful! Redirecting to login...
          </div>
          <button
            type="button"
            class="btn-close btn-close-white me-2 m-auto"
            @click="showToast = false"
          ></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const form = reactive({
  email: '',
  password: '',
  full_name: '',
  qualification: '',
  dob: ''
})
const errors = reactive({
  full_name: '',
  email:     '',
  password:  '',
  dob:       ''
})
const serverError = ref('')
const showToast = ref(false)
const router = useRouter()
const registering = ref(false)

// Computed validity
const isFormValid = computed(() =>
  form.full_name.trim() !== '' &&
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email) &&
  form.password.length >= 6 &&
  (!form.dob || new Date(form.dob) <= new Date())
)

// Single validator for multiple fields
function validateField(field) {
  switch (field) {
    case 'full_name':
      errors.full_name = form.full_name.trim()
        ? ''
        : 'Full name is required'
      break
    case 'email':
      if (!form.email.trim()) {
        errors.email = 'Email is required'
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
        errors.email = 'Invalid email'
      } else {
        errors.email = ''
      }
      break
    case 'password':
      if (!form.password) {
        errors.password = 'Password is required'
      } else if (form.password.length < 6) {
        errors.password = 'At least 6 characters'
      } else {
        errors.password = ''
      }
      break
    case 'dob':
      if (form.dob && new Date(form.dob) > new Date()) {
        errors.dob = 'Cannot be in the future'
      } else {
        errors.dob = ''
      }
      break
  }
}

async function register() {
  serverError.value = ''

  validateField('full_name')
  validateField('email')
  validateField('password')
  validateField('dob')

  if (!isFormValid.value) {
    return
  }

  registering.value = true
  try {
    const res = await axios.post('/api/auth/register', form)
    const token = res.data.access_token
    localStorage.setItem('access_token', token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`

    // ✅ Show toast and redirect after delay
    showToast.value = true
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (e) {
    console.error('Registration error:', e.response?.data || e.message)
    serverError.value =
      e.response?.data?.msg ||
      e.response?.data?.error ||
      e.message ||
      'Registration failed'
  } finally {
    registering.value = false
  }
}
</script>

<style scoped>
.registration-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-width: 95vw;
  min-height: 95vh;
  background: #ffffff;
  padding: 1rem;
  margin-left:-7rem;
  margin-top:-0.5rem;
  overflow: hidden;
}

.registration-card {
  width: 100%;
  min-width: 900px;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  /* align-items: center; */
  justify-content: center;
}

.card-title {
  font-size: 2.2rem;
  font-weight: 700;
  color: #333333;
}

.form-label {
  font-weight: 500;
  color: #495057;
}

.btn-primary {
  background-color: #007bff;
  border-color: #007bff;
}

.btn-primary:hover {
  background-color: #0056b3;
  border-color: #0056b3;
}

.alert {
  font-size: 0.9rem;
}
</style>


