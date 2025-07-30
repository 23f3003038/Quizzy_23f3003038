<template>
  <div class="container-fluid py-4">
    <h2 class="mb-4">Upcoming Quizzes</h2>

    <div v-if="upcoming.length" class="card shadow-sm">
      <div class="card-body p-3">
        <div class="table-responsive">
          <table class="table table-bordered table-striped align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th style="width: 3rem;">#</th>
                <th>Quiz Title</th>
                <th style="width: 10rem;">Subject</th>
                <th style="width: 14rem;">Deadline (IST)</th>
                <th style="width: 8rem;">Duration</th>
                <th style="width: 8rem;">Questions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(q, i) in upcoming" :key="q.id">
                <td>{{ i + 1 }}</td>
                <td>{{ q.name }}</td>
                <td>{{ q.subject_name || '—' }}</td>
                <td>{{ formatIST(q.deadline) }}</td>
                <td>{{ formatDuration(q.duration) }}</td>
                <td>{{ q.total_questions }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-else class="text-center text-muted py-5">
      No upcoming quizzes scheduled.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const upcoming = ref([])

onMounted(async () => {
  try {
    const { data: all } = await axios.get('/api/admin/quizzes')
    const now = new Date()

    // filter + sort
    const future = all
      .filter(q => q.deadline && new Date(q.deadline) > now)
      .sort((a, b) => new Date(a.deadline) - new Date(b.deadline))

    // enrich with subject name & question count
    upcoming.value = await Promise.all(
      future.map(async q => {
        const { data: details }    = await axios.get(`/api/admin/quizzes/${q.id}`)
        const { data: questions }  = await axios.get(`/api/admin/quizzes/${q.id}/questions`)
        return {
          ...q,
          subject_name:   details.subject_name,
          total_questions: questions.length
        }
      })
    )
  } catch (err) {
    console.error('Failed to fetch upcoming quizzes:', err)
  }
})

function formatIST(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('en-IN', {
    timeZone: 'Asia/Kolkata',
    year:   'numeric',
    month:  'short',
    day:    'numeric',
    hour:   '2-digit',
    minute: '2-digit'
  })
}

function formatDuration(dur) {
  if (!dur) return '—'
  const [h, m] = dur.split(':').map(Number)
  return [
    h ? `${h}h` : null,
    m ? `${m}m` : null
  ].filter(Boolean).join(' ') || '0m'
}
</script>

<style scoped>
.card {
  border-radius: 8px;
}
.table th,
.table td {
  vertical-align: middle;
}
</style>
