<template>
  <div class="d-flex vh-100 overflow-hidden" style="background: white; min-width: 100vw; margin-left:-10rem;">
    <!-- Sidebar -->
    <aside class="text-white p-3" style="width: 250px; background: linear-gradient(to bottom, #000, #14518f, #000); color:#f8f9fa;">
      <div class="d-flex align-items-center justify-content-center mb-4">
        <img src="/logo.png" alt="Logo" class="me-2 logo-slide" style="height: 40px; width: 40px; object-fit: contain;" />
        <h4 class="m-0">Quizzy</h4>
      </div>
      <nav class="nav flex-column">
        <router-link to="/admin" class="nav-link text-white" exact-active-class="active">Dashboard</router-link>
        <router-link to="/admin/users" class="nav-link text-white" active-class="active">Users</router-link>
        <router-link to="/admin/subjects" class="nav-link text-white" active-class="active">Subjects</router-link>
        <router-link to="/admin/reports" class="nav-link text-white" active-class="active">Reports</router-link>
        <a @click.prevent="logout" class="nav-link text-white mt-3">Logout</a>
      </nav>
    </aside>

    <!-- Main content -->
    <div class="flex-fill d-flex flex-column">
      <!-- Topbar -->
      <header class="d-flex justify-content-between align-items-center bg-white px-4 py-2 border-bottom">
        <!-- Left: Search -->
        <div class="d-flex align-items-center">
          <div class="input-group custom-search">
            <span class="input-group-text bg-white border-end-0">
              <i class="bi bi-search text-muted"></i>
            </span>
            <input
              v-model="searchTerm"
              type="text"
              class="form-control border-start-0 no-focus-outline"
              placeholder="Search..."
            />
          </div>
        </div>

        <!-- Right: Profile with hover dropdown -->
        <div class="profile-dropdown position-relative ms-3">
          <div class="d-flex align-items-center profile-trigger hover-slide">
            <i class="bi bi-person-circle fs-3 me-2 profile icon"></i>
            <span class="fw-semibold">Quizzy Admin</span>
          </div>

          <div class="dropdown-menu profile-info shadow-sm p-3 bg-white position-absolute end-0 mt-2 rounded">
            <p class="mb-1"><strong>Name:</strong> {{ admin.name }}</p>
            <p class="mb-1"><strong>Email:</strong> {{ admin.email }}</p>
            <p class="mb-0"><strong>Qualification:</strong> {{ admin.qualification }}</p>
          </div>
        </div>
      </header>

      <!-- Routed views -->
      <main class="overflow-auto p-4">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ref, watch , onMounted} from 'vue'
import axios from 'axios'

const router = useRouter()
const searchTerm = ref('')

const admin = ref({
  name: '',
  email: '',
  qualification: ''
})

// Fetch real admin info from backend
onMounted(async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/admin/me', { withCredentials: true })
    admin.value = res.data
  } catch (err) {
    console.error('Failed to load admin info:', err)
  }
})

// Emit search term globally for listening components
watch(searchTerm, (val) => {
  const routeName = router.currentRoute.value.name
  window.dispatchEvent(new CustomEvent('admin-search', { detail: { value: val, route: routeName } }))
})

function logout() {
  localStorage.removeItem('access_token')
  router.push({ name: 'landing' })
}
</script>

<style scoped>
.nav-link.active {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 0.25rem;
}

.custom-search {
  width: 450px;
}

.no-focus-outline:focus {
  box-shadow: none !important;
  border-color: #ced4da !important;
}

/* Profile dropdown: initially hidden, slides left on hover */
.profile-dropdown .dropdown-menu {
  display: none;
  min-width: 250px;
  z-index: 1000;
  border: 1px solid #ddd;
  transform: translateX(0);
  transition: transform 0.2s ease;
}

.profile-dropdown:hover .profile-icon {
  color: #000 
}

.profile-dropdown:hover .dropdown-menu {
  display: block;
  background: linear-gradient(to bottom, #14528f08, #0000000c); 
  color:#000000;
  transform: translateX(-10px);
}

/* Slide effect on logo */
.logo-slide {
  transition: transform 0.2s ease;
}

.logo-slide:hover {
  transform: translateX(-5px);
}

/* Slide effect on profile icon + text */
.hover-slide {
  transition: transform 0.2s ease;
}

.hover-slide:hover {
  transform: translateX(-55px) scale(1.1);
}
</style>
