// src/main.js

import './assets/main.css'

import axios from 'axios'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import 'bootstrap/dist/css/bootstrap.min.css'
import App from './App.vue'
import router from './router'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

import 'chartjs-adapter-date-fns'

// ——— Axios global configuration ———
axios.defaults.baseURL = 'http://localhost:5000'
const token = localStorage.getItem('access_token')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

// ——— Create and mount Vue app ———
const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
