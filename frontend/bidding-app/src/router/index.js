import { createRouter, createWebHistory } from 'vue-router'
import { authService } from '@/services/auth'
import Dashboard from '@/components/bidding/Dashboard.vue'
import Auctions from '@/components/bidding/Auctions.vue'
import CreateBid from '@/components/bidding/CreateBid.vue'
import BidInterface from '@/components/bidding/BidInterface.vue'
import LoginForm from '../components/auth/LoginForm.vue'
import RegisterForm from '../components/auth/RegisterForm.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginForm,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterForm,
    meta: { requiresGuest: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/auctions',
    name: 'Auctions',
    component: Auctions,
    meta: { requiresAuth: true }
  },
  {
    path: '/create-bid',
    name: 'CreateBid',
    component: CreateBid,
    meta: { requiresAuth: true }
  },
  {
    path: '/bid/:groupName',
    name: 'BidInterface',
    component: BidInterface,
    meta: { requiresAuth: true },
    props: true
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
