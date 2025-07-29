<template>
  <div class="login-wrapper">
    <div class="card login-card shadow-lg">
      <div class="row g-0" style="min-height: 95vh">
        <!-- Image Column (Left) -->
        <div class="image col-12 col-md-6 d-none d-md-block">
          <img
            src="/Login.png"
            alt="Login illustration"
            class="img-fluid h-100 w-100"
            style="object-fit: cover; border-radius: 2rem 0 0 2rem"
          />
        </div>

        <!-- Form Column (Right) -->
        <div class="col-12 col-md-6 p-4">
          <h2 class="card-title text-center mb-4">Welcome Back</h2>
          <span class="text-muted">Please login to your account</span>
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input v-model="full_name" @blur="validateFullName" @input="validateFullName" type="text" placeholder="Enter full name" class="form-control" :class="{ 'is-invalid': errors.full_name }" />
            <div v-if="errors.full_name" class="invalid-feedback">
              {{ errors.full_name }}
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="email" @blur="validateEmail" @input="validateEmail" type="email" placeholder="abc@gmail.com" class="form-control" :class="{ 'is-invalid': errors.email }" />
            <div v-if="errors.email" class="invalid-feedback">
              {{ errors.email }}
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="password" @blur="validatePassword" @input="validatePassword" type="password" class="form-control" :class="{ 'is-invalid': errors.password }" />
            <div v-if="errors.password" class="invalid-feedback">
              {{ errors.password }}
            </div>
          </div>
          <button class="btn btn-primary w-100" @click="login" :disabled="!isFormValid || submitting">Login</button>
          <div v-if="serverError" class="alert alert-danger mt-3 text-center">{{ serverError }}</div>
          <p class="mt-3 text-center">Don't have an account?
            <router-link to="/register" class="text-decoration-none">
              Create one
            </router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const full_name = ref('')
const email = ref('')
const password = ref('')
const serverError = ref('')
const errors = reactive({
  full_name: '',
  email: '',
  password: ''
})
const submitting = ref(false) 
const router = useRouter()

// Computed flag
const isFormValid = computed(() =>
  full_name.value.trim() !== '' &&
  email.value.trim()     !== '' &&
  password.value.trim()  !== ''
)

// Field validators
function validateFullName() {
  errors.full_name = full_name.value.trim()
    ? ''
    : 'Full name is required'
}
function validateEmail() {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!email.value.trim()) {
    errors.email = 'Email is required'
  } else if (!re.test(email.value)) {
    errors.email = 'Invalid email format'
  } else {
    errors.email = ''
  }
}
function validatePassword() {
  if (!password.value) {
    errors.password = 'Password is required'
  } else if (password.value.length < 6) {
    errors.password = 'At least 6 characters'
  } else {
    errors.password = ''
  }
}

async function login() {
  serverError.value = ''
  validateFullName(); validateEmail(); validatePassword()

  if (!isFormValid.value) return

  submitting.value = true
  try {
    const res = await axios.post('/api/auth/login', {
      full_name: full_name.value,
      email:      email.value,
      password:   password.value
    })
    localStorage.setItem('access_token', res.data.access_token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`
    router.push({ name: 'admin-dashboard' })
  } catch (e) {
    serverError.value = e.response?.data?.msg || 'Login failed'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-width: 100vw;
  min-height: 100vh;
  background: #ffffff;
  padding: 1rem;
  overflow: hidden;
  margin-left:-10rem;
}

.login-card {
  width: 100%;
  min-width: 900px;
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
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

.text-muted{
  display:flex;
  justify-content: center;
  margin-top:-1.5rem;
  font-size:1.2rem;
}
</style>
