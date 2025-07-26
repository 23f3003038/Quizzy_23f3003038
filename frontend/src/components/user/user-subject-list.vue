<template>
  <div class="container py-4">
    <!-- Page Title -->
    <h2 class="fw-bold mb-1">Subjects</h2>
    <p class="text-muted mb-4">Explore subjects and dive into quizzes</p>

    <!-- Subject Cards -->
    <div class="row g-4">
      <div
        class="col-md-4"
        v-for="subject in filteredSubjects"
        :key="subject.id"
      >
        <div
          class="subject-card shadow-sm rounded overflow-hidden"
          @click="goToSubjectDetails(subject.id)"
        >
          <!-- Image with overlay -->
          <div class="subject-image position-relative">
            <img
              src="/user-subjectbg.png"
              alt="Subject"
              class="w-100 h-100 object-fit-cover"
            />
            <div
              class="overlay position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
            >
              <h1 class="text-white fw-bold text-center">
                {{ subject.name }}
              </h1>
            </div>
          </div>
          <!-- Description -->
          <div class="p-3 description-area">
            <p class="mb-0 text-muted line-clamp">
              {{ subject.description }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- No Subjects -->
    <div v-if="filteredSubjects.length === 0" class="text-center text-muted mt-4">
      No subjects found.
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const subjects = ref([])
const filteredSubjects = ref([])
const router = useRouter()

function fetchSubjects() {
  axios.get('/api/user/subjects')
    .then(res => {
      subjects.value = res.data
      filteredSubjects.value = res.data
    })
    .catch(err => {
      console.error('❌ Failed to fetch subjects', err)
    })
}

function goToSubjectDetails(id) {
  router.push(`/user/subjects/${id}`)
}

function handleSearch(e) {
  const term = e.detail.value.toLowerCase()
  filteredSubjects.value = subjects.value.filter(subject =>
    subject.name?.toLowerCase().includes(term) ||
    subject.description?.toLowerCase().includes(term)
  )
}

onMounted(() => {
  fetchSubjects()
  window.addEventListener('user-search', handleSearch)
})

onBeforeUnmount(() => {
  window.removeEventListener('user-search', handleSearch)
})
</script>

<style scoped>
.subject-card {
  background-color: #ffffff;
  border: 1px solid #e0e0e0;
  transition: transform 0.2s ease-in-out;
  height: 320px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.subject-card:hover {
  transform: translateY(-4px) scale(1.05);
  background: rgba(43, 122, 119, 0.029);
  cursor: pointer;
}

.subject-image {
  height: 160px;
  overflow: hidden;
  position: relative;
}

.object-fit-cover {
  object-fit: cover;
}

.overlay {
  background: rgba(122, 121, 43, 0.551);
  color: white;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.6);
}

.description-area {
  height: 120px;
  overflow: hidden;
}

.line-clamp {
  height: auto;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-clamp: 3;
  box-orient: vertical;
}
</style>
