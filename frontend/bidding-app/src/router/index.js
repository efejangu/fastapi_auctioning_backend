import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '@/services/auth'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../components/auth/LoginForm.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../components/auth/RegisterForm.vue'),
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../components/bidding/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/auctions',
    name: 'Auctions',
    component: () => import('../components/bidding/Auctions.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// Navigation Guards
router.beforeEach((to, from, next) => {
  const isAuthenticated = authService.isAuthenticated()

  if (to.meta.requiresAuth && !isAuthenticated) {
    // Redirect to login if trying to access protected route
    next('/login')
  } else if (to.meta.requiresGuest && isAuthenticated) {
    // Redirect to dashboard if authenticated user tries to access login/register
    next('/dashboard')
  } else {
    next()
  }
})

export default router
