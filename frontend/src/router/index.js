// frontend/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'
import Landing from '@/views/Landing.vue'
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
import userLayout from '@/components/user/user-layout.vue'
import userDashboard from '@/components/user/user-dashboard.vue'
import userSubjectList from '@/components/user/user-subject-list.vue'
import userSubjectDetails from '@/components/user/user-subject-details.vue'
import userChapterDetails from '@/components/user/user-chapter-details.vue'
import userQuizDetails from '@/components/user/user-quiz-details.vue'
import userQuizInstructions from '@/components/user/user-quiz-instructions.vue'
import userQuizAttempt from '@/components/user/user-quiz-attempt.vue'
import userQuizResult from '@/components/user/user-quiz-result.vue'
import userQuizReport from '@/components/user/user-quiz-report.vue'
import UserQuizzesList  from '@/components/user/UserQuizzesList.vue'

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

  {
    path: '/user',
    name: 'user',
    component: userLayout,
    meta: { requiresAuth: true, role: 'user' },
    children: [
      { path: '', name: 'user-dashboard', component: userDashboard },
      { path: 'dashboard', name: 'user-dashboard-alias', component: userDashboard},
      { path: 'subjects', name: 'UserSubjects', component: userSubjectList},
      { path: 'subjects/:id', name: 'UserSubjectDetails', component: userSubjectDetails},
      { path: 'chapters/:id/details', name: 'UserChapterDetails', component: userChapterDetails, props: true },
      { path: 'quiz/:quizId',  name: 'UserQuizDetails', component: userQuizDetails},
      { path: 'quiz/:quizid/attempt', name: 'UserQuizAttemptInstructions', component: userQuizInstructions, props: true},
      { path: 'quiz/:quizId/attempt/live', name: 'UserQuizAttempt', component: userQuizAttempt, props: true},
      { path: 'quiz/attempt/:attemptId/result', name: 'UserQuizResult', component: userQuizResult, props: true},
      { path: 'report',         name: 'user-report',     component: userQuizReport },
      { path: 'quizzes', name: 'UserQuizzes', component: UserQuizzesList }, 
      { path: 'report/:scoreId', name: 'UserQuizReport', component: userQuizReport, props: true }
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
    return next({ name: 'user-dashboard' }) // 🚫 block user from admin area
  }

  if (to.meta.role === 'user' && user?.is_admin === true) {
    return next({ name: 'admin-dashboard' }) // 🚫 block admin from user area
  }

  next()
})

export default router
