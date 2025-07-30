<template>
  <div v-if="!isLoaded" class="container py-4 text-center">
    Loading subject details…
  </div>
  <div v-else class="container py-4">
    <!-- Back link -->
    <div class="mb-3 d-flex align-items-center cursor-pointer" @click="goBack">
      <i class="bi bi-arrow-left me-2"></i> Back
    </div>

    <!-- Breadcrumb -->
    <div class="text-muted mb-3">
      Subjects / <strong>{{ subject?.name }}</strong>
    </div>

    <!-- Subject Info Box -->
    <div class="d-flex align-items-start gap-3 mb-4 p-3 border rounded shadow-sm">
      <div class="initials-box">{{ initials }}</div>
      <div>
        <h4 class="mb-1">{{ subject?.name }}</h4>
        <p class="text-muted">{{ subject?.description }}</p>
        <div class="d-flex gap-2">
          <button class="btn btn-sm btn-secondary" @click="openForm">Edit</button>
          <button class="btn btn-sm btn-danger" @click="removeSubject">Delete</button>
        </div>
      </div>
    </div>

    <!-- Add Chapter Button -->
    <div class="mb-3 text-end">
      <button class="btn btn-primary" @click="openChapterForm()">+ Add Chapter</button>
    </div>

    <!-- Total Chapters -->
    <div class="mb-2 fw-bold">Total Chapters: {{ filteredChapters.length }}</div>

    <!-- Chapters Table -->
    <div class="table-responsive">
      <table class="table table-hover table-fixed" v-if="filteredChapters.length > 0">
        <thead>
          <tr>
            <th>Chapter Name</th>
            <th>Description</th>
            <th>Quizzes</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="chap in filteredChapters" :key="chap.id">
            <td>{{ chap.name }}</td>
            <td>{{ chap.description }}</td>
            <td>{{ chap.quizCount }}</td>
            <td>
              <button class="btn btn-sm btn-outline-primary me-2" @click="viewChapter(chap)">View</button>
              <button class="btn btn-sm btn-outline-secondary me-2" @click="editChapter(chap)">Edit</button>
              <button class="btn btn-sm btn-outline-danger" @click="deleteChapter(chap.id)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- No Results -->
      <div v-else class="text-center text-muted py-4">
        No chapters found.
      </div>
    </div>

    <!-- Forms -->
    <SubjectForm 
      v-if="showSubjectForm" 
      :subject="subject" 
      @saved="fetchSubject" 
      @close="showSubjectForm = false" 
    />

    <ChapterForm 
      v-if="showChapterForm" 
      :chapter="editingChapter" 
      :subjectId="Number(subjectId)"
      :subject-name="subject?.name"
      @saved="fetchChapters" 
      @close="showChapterForm = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

import SubjectForm from './subject-form.vue'
import ChapterForm from './chapter-form.vue'

const route = useRoute()
const router = useRouter()
const subjectId = route.params.id


const subject = ref(null)
const chapters = ref([])
const filteredChapters = ref([])

const showSubjectForm = ref(false)
const showChapterForm = ref(false)
const editingChapter = ref(null)

const isLoaded = computed(() => subject.value !== null) 

const initials = computed(() => {
  if (!subject.value?.name) return ""
  return subject.value.name
    .split(" ")
    .map(word => word[0])
    .join("")
    .substring(0, 2)
    .toUpperCase()
})

function goBack() {
  router.push('/admin/subjects')
}

function fetchSubject() {
  axios.get(`/api/admin/subjects/${subjectId}`).then(res => {
    subject.value = res.data
  })
}

async function fetchChapters() {
  const res = await axios.get(`/api/admin/subjects/${subjectId}/chapters`)
  const chaps = res.data
  for (const c of chaps) {
    const qres = await axios.get(`/api/admin/chapters/${c.id}/quizzes`)
    c.quizCount = qres.data.length
  }
  chapters.value = chaps
  filteredChapters.value = chaps
}

function openForm() {
  showSubjectForm.value = true
}

function viewChapter(chap) {
  router.push(`/admin/chapters/${chap.id}/details`)
}

function removeSubject() {
  axios.delete(`/api/admin/subjects/${subjectId}`).then(() => {
    router.push("/admin/subjects")
  })
}

function openChapterForm(chap = null) {
  editingChapter.value = chap
  showChapterForm.value = true
}

function editChapter(chap) {
  openChapterForm(chap)
}

function deleteChapter(id) {
  axios.delete(`/api/admin/chapters/${id}`).then(fetchChapters)
}

onMounted(() => {
  fetchSubject()
  fetchChapters()

  // Listen to global search event
  window.addEventListener('admin-search', (e) => {
    const term = e.detail.value.toLowerCase()
    filteredChapters.value = chapters.value.filter(chap =>
      chap.name?.toLowerCase().includes(term) ||
      chap.description?.toLowerCase().includes(term)
    )
  })
})
</script>

<style scoped>
.initials-box {
  width: 100px;
  height: 100px;
  background-color: #14518f;
  color: #fff;
  font-size: 24px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  padding: 3.2rem;
}

.cursor-pointer {
  cursor: pointer;
}

.table  th{
  font-weight: bold
}

.table-fixed {
  table-layout: fixed;
  width: 100%;
}

/* 2. ellipsis on overflow */
.table-fixed th,
.table-fixed td {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 3. assign each column a percentage */
.table-fixed th:nth-child(1),
.table-fixed td:nth-child(1) {
  width: 25%;   /* Chapter Name */
}
.table-fixed th:nth-child(2),
.table-fixed td:nth-child(2) {
  width: 45%;   /* Description */
}
.table-fixed th:nth-child(3),
.table-fixed td:nth-child(3) {
  width: 20%;   /* Quizzes */
}
.table-fixed th:nth-child(4),
.table-fixed td:nth-child(4) {
  width: 20%;   /* Actions */
}

</style>
