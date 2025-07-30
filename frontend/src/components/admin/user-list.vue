<template>
  <div class="p-4">
    <h3 class="mb-2 fw-bold">All Users</h3>
    <p class="mb-4 text-muted">Total Students: {{ studentCount }}</p>

    <table class="table table-hover align-middle">
      <thead class="table-light">
        <tr>
          <th>Name</th>
          <th>Email</th>
          <th>DOB</th>
          <th>Qualification</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="students.length === 0">
          <td colspan="5" class="text-center text-muted py-3">
            No user found.
          </td>
        </tr>
        <tr v-for="u in students" :key="u.id">
          <td>{{ u.full_name }}</td>
          <td>{{ u.email }}</td>
          <td>{{ u.dob ? new Date(u.dob).toLocaleDateString() : '—' }}</td>
          <td>{{ u.qualification || '—' }}</td>
          <td>
            <router-link
              :to="{ name: 'user-details', params: { id: u.id } }"
              class="btn btn-sm btn-outline-primary custom-hover" 
            >
              View Details
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const users = ref([])
const filteredUsers = ref([])

const students = computed(() =>
  filteredUsers.value.filter(u => !u.is_admin)
)
const studentCount = computed(() => students.value.length)

onMounted(() => {
  axios.get('/api/admin/users', { withCredentials: true })
    .then(res => {
      users.value = res.data
      filteredUsers.value = res.data
    })
    .catch(err => {
      console.error('Failed to fetch users:', err)
    })

  // Listen for global search input from admin layout
  window.addEventListener('admin-search', (e) => {
    const term = e?.detail?.value?.toLowerCase?.() || ''
    filteredUsers.value = users.value.filter(user =>
      user.full_name?.toLowerCase().includes(term) ||
      user.email?.toLowerCase().includes(term)
    )
  })
})
</script>

<style scoped>
.table th,
.table td {
  vertical-align: middle;
}

.custom-hover:hover {
  background-color:  #0a3158 ;
  color: white ;
  border-color: black ;
}

</style>
