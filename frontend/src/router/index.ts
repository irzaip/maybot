import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const routes = [
  { path: '/', name: 'Login', component: Login },
  { path: '/admin', name: 'Admin', component: AdminDashboard }
]

const router = createRouter({
  history: createWebHistory('/'),
  routes
})

export default router