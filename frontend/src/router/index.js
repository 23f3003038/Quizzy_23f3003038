// frontend/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'
import Landing from '@/views/landing.vue'
import Login from '@/components/auth/Login.vue'
import Register from '@/components/auth/Register.vue'
import AdminLayout from '@/components/admin/admin-layout.vue'
import AdminDashboard from '@/components/admin/dashboard.vue'
import SubjectList from '@/components/admin/subject-list.vue'
import ChapterList from '@/components/admin/chapter-list.vue'
import QuizList from '@/components/admin/quiz-list.vue'
import QuestionList from '@/components/admin/question-list.vue'
import UserList from '@/components/admin/user-list.vue'
import Report from '@/components/admin/report.vue'
import userDetails from '@/components/admin/user-details.vue'
import upcomingQuiz from '@/components/admin/upcoming-quiz.vue'
import subjectDetails from '@/components/admin/subject-details.vue'
import chapterDetails from '@/components/admin/chapter-details.vue'
import quizDetails from '@/components/admin/quiz-details.vue'

const routes = [
  { path: '/', name: 'landing', component: Landing },
  { path: '/login', name: 'login', component: Login },
  { path: '/register', name: 'register', component: Register },

  {
    path: '/admin',
    name: 'admin',
    component: AdminLayout,
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      { path: '', name: 'admin-dashboard', component: AdminDashboard},
      { path: 'subjects', name: 'subjects',  component: SubjectList },
      { path: 'chapters',   name: 'chapters',  component: ChapterList,  props: true },
      { path: 'quizzes',    name: 'quizzes',   component: QuizList,     props: true },
      { path: 'questions',   name: 'questions', component: QuestionList, props: true },
      { path: 'users', name: 'users', component: UserList },
      { path: 'reports', name: 'report', component: Report },
      { path: 'users/:id', name: 'user-details', component: userDetails, props: true },
      { path: 'upcoming-quizzes', name: 'upcoming-quizzes', component: upcomingQuiz },
      { path: 'subjects/:id', name: 'subject-details', component: subjectDetails, props: true },
      { path: 'chapters/:id/details', name: 'chapter-details', component: chapterDetails, props: true},
      { path: 'quizzes/:id/details', name: 'quiz-details', component:quizDetails, props: true}
    ]
  },

  // fallback
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const user = token
    ? JSON.parse(atob(token.split('.')[1]))
    : null

  if (to.meta.requiresAuth && !token) {
    return next({ name: 'login' })
  }
  if (to.meta.role === 'admin' && user?.is_admin !== true) {
    return next({ name: 'home' })
  }
  next()
})

export default router
