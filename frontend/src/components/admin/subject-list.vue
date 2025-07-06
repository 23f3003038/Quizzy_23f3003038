<template>
  <div class="container py-4">

    <!-- Heading -->
    <h2 class="text-center fw-bold mb-3">Subjects</h2>

    <!-- Add Subject Button -->
    <div class="text-center mb-3">
      <button class="btn btn-sm custom-hover px-3" style="" @click="openForm()">+ Add Subject</button>
    </div>

    <!-- Subject Cards Grid -->
    <div class="row mb-4 gy-5">
      <div class="col-md-4 mb-3" style="padding:0.5rem" v-for="s in filteredSubjects" :key="s.id" >
        <div class="card shadow-sm subject-card" @click="goToChapters(s)">
          <div class="subject-image" :style="{ backgroundImage: `url('/Subjectbg.png')` }" >
            <div class="subject-name-overlay">
              <span>{{ s.name }}</span>
            </div>
          </div>
          <div class="card-body">
            <p class="card-text subject-desc text-muted">{{ s.description }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Subject Form -->
    <SubjectForm 
      v-if="showForm" 
      :subject="current" 
      @saved="fetch()" 
      @close="showForm=false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import SubjectForm from './subject-form.vue'

const subjects = ref([])
const filteredSubjects = ref([])
const showForm = ref(false)
const current = ref(null)
const router = useRouter()

function fetch() {
  axios.get('/api/admin/subjects').then(r => {
    subjects.value = r.data
    filteredSubjects.value = r.data
  })
}

function openForm(subj = null) {
  current.value = subj
  showForm.value = true
}

function goToChapters(s) {
  router.push(`/admin/subjects/${s.id}`)
}

onMounted(() => {
  fetch()

  // Listen to global search bar event
  window.addEventListener('admin-search', (e) => {
    const term = e.detail.value.toLowerCase()
    filteredSubjects.value = subjects.value.filter(subject =>
      subject.name?.toLowerCase().includes(term) ||
      subject.description?.toLowerCase().includes(term)
    )
  })
})
</script>

<style scoped>
.custom-hover{
  border: 1px solid #0a3158;
  color: #0a3158;
}

.custom-hover:hover {
  background-color:  #0a3158 ;
  color: white ;
  border-color: black ;
}

.subject-card {
  cursor: pointer;
  transition: transform 0.2s;
  height: 120%; /* full height card */
  width:85%;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap:0.5rem;
}

.subject-card:hover {
  transform: scale(1.02);
}

.subject-image {
  background-size: cover;
  background-position: center;
  height: 180px;
  position: relative;
  border-top-left-radius: 0.375rem;
  border-top-right-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.subject-name-overlay {
  color: white;
  width: 100%;
  padding: 0.5rem;
  text-align: center;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
}

.subject-name-overlay span {
  font-weight: 700;
  font-family: 'Times New Roman', Times, serif;
  font-size: clamp(2.5rem, 2vw, 2rem);
  display: inline-block;
  max-width: 90%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.subject-desc {
  height: auto;
  display: -webkit-box;           /* Fallback for Safari, Chrome */
  -webkit-line-clamp: 3;          /* Limit to 3 lines */
  -webkit-box-orient: vertical;   /* Required for line-clamp */
  overflow: hidden;               /* Hide overflowing content */
  text-overflow: ellipsis;        /* Add '...' */
  line-clamp: 3;                  /* Not fully supported yet, but future-proof */
  box-orient: vertical;           /* Not yet standard, but included for consistency */
}
</style>
