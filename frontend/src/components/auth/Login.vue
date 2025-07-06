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
            <input v-model="full_name" type="text" placeholder="Enter full name" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="email" type="email" placeholder="abc@gmail.com" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" />
          </div>
          <button class="btn btn-primary w-100" @click="login">Login</button>
          <div v-if="error" class="alert alert-danger mt-3 text-center">{{ error }}</div>
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
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const full_name = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

async function login() {
  error.value = ''
  try {
    const res = await axios.post('/api/auth/login', {
      full_name: full_name.value,
      email: email.value,
      password: password.value
    })
    localStorage.setItem('access_token', res.data.access_token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${res.data.access_token}`
    router.push({ name: 'admin-dashboard' })
  } catch (e) {
    error.value = e.response?.data?.msg || 'Login failed'
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
