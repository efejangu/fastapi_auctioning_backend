import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../components/auth/LoginForm.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../components/auth/RegisterForm.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../components/bidding/Dashboard.vue')
  },
  {
    path: '/auctions',
    name: 'Auctions',
    component: () => import('../components/bidding/Auctions.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
