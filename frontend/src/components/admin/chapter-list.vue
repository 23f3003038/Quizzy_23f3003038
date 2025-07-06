<template>
  <div>
    <h3>Chapters</h3>
    <button class="btn btn-primary mb-2" @click="openForm()">+ New Chapter</button>
    <table class="table">
      <thead><tr><th>Name</th><th>Description</th><th>Actions</th></tr></thead>
      <tbody>
        <tr v-for="c in filteredChapters" :key="c.id">
          <td @click="goToQuizzes(c)">{{ c.name }}</td>
          <td>{{ c.description }}</td>
          <td>
            <button class="btn btn-sm btn-secondary" @click="openForm(c)">Edit</button>
            <button class="btn btn-sm btn-danger" @click="remove(c.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
    <ChapterForm
      v-if="showForm"
      :chapter="current"
      :subjectId="id"
      @saved="fetch()"
      @close="showForm = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import ChapterForm from './chapter-form.vue'

const props = defineProps({ id: Number })
const chapters = ref([])
const filteredChapters = ref([])
const showForm = ref(false)
const current = ref(null)
const router = useRouter()

function fetch() {
  axios.get(`/api/admin/subjects/${props.id}/chapters`).then(r => {
    chapters.value = r.data
    filteredChapters.value = r.data
  })
}

function openForm(chap = null) {
  current.value = chap
  showForm.value = true
}

function remove(id) {
  axios.delete(`/api/admin/chapters/${id}`).then(fetch)
}

function goToQuizzes(chap) {
  router.push(`/admin/chapters/${chap.id}/quizzes`)
}

onMounted(() => {
  fetch()

  window.addEventListener('admin-search', (e) => {
    const term = e.detail.value.toLowerCase()
    filteredChapters.value = chapters.value.filter(chap =>
      chap.name?.toLowerCase().includes(term) ||
      chap.description?.toLowerCase().includes(term)
    )
  })
})
</script>
