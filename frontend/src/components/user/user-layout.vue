<template>
  <div class="user-layout d-flex" style="min-width: 100vw; margin-left: -10rem">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header text-center py-3 fw-bold fs-4 text-white border-bottom">
        <img src="/logo.png" alt="Logo" class="topbar-logo" />
        Quizzy
      </div>
      <nav class="nav-links d-flex flex-column px-3 pt-3">
        <RouterLink to="/user" class="nav-item" exact-active-class="active">Dashboard</RouterLink>
        <RouterLink to="/user/subjects" class="nav-item" exact-active-class="active">Subjects</RouterLink>
        <RouterLink to="/user/quizzes" class="nav-item" exact-active-class="active">Quizzes</RouterLink>
        <RouterLink to="/user/report" class="nav-item" exact-active-class="active">Report</RouterLink>
        <button class="nav-item logout mt-auto" @click="logout">Logout</button>
      </nav>
    </aside>

    <!-- Main Content -->
    <div class="main-area flex-grow-1 d-flex flex-column">
      <!-- Topbar -->
      <header class="topbar d-flex justify-content-between align-items-center px-4 py-3">
        <div class="left">
          <input
              v-model="searchTerm"
              type="text"
              class="form-control border-start-0 no-focus-outline"
              placeholder="Search..."
            />
        </div>
        <div class="right d-flex align-items-center gap-2">
          <img src="/logo.png" alt="Logo" class="topbar-logo" />
          <span class="fw-semibold text-white">Welcome User</span>
        </div>
      </header>

      <!-- Router View -->
      <main class="main-container p-4">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchTerm = ref('') 

// Emit search term globally for listening components
watch(searchTerm, (val) => {
  const routeName = router.currentRoute.value.name
  window.dispatchEvent(new CustomEvent('user-search', { detail: { value: val, route: routeName } }))
})

function logout() {
  router.push('/login')
}
</script>

<style scoped>
.user-layout {
  height: 100vh;
  background: white;
  font-family: 'Segoe UI', sans-serif;
}

.sidebar {
  width: 220px;
  background: linear-gradient(to bottom, #337665, #7baa73, #fac126);
  color: white;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.sidebar-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.nav-links {
  flex: 1;
  gap: 10px;
}

.nav-item {
  display: block;
  width: 100%;
  padding: 10px 15px;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  font-weight: 500;
  transition: background-color 0.2s;
}

.nav-item:hover,
.nav-item.active {
  background-color: rgba(83, 92, 88, 0.5);
}

.logout {
  background: none;
  border: none;
  text-align: left;
  color: rgb(0, 0, 0);
  font-weight: 500;
  cursor: pointer;
}

.topbar {
  background: linear-gradient(to right, #337665, #7baa73, #fac126);
  color: white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.search-input {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  width: 250px;
  outline: none;
}

.topbar-logo {
  height: 36px;
  width: auto;
}

.main-container {
  flex: 1;
  overflow-y: auto;
}
</style>
