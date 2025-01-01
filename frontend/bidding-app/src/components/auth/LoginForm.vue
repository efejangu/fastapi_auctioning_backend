<template>
  <div class="login-container">
    <form @submit.prevent="handleSubmit" class="login-form">
      <h1 class="title">BidFlow</h1>
      <div class="form-group">
        <input
          type="text"
          v-model="username"
          placeholder="Username"
          required
        />
      </div>

      <div class="form-group">
        <input
          type="password"
          v-model="password"
          placeholder="Password"
          required
        />
      </div>

      <button type="submit" :disabled="loading" class="submit-btn">
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>

      <div v-if="error" class="error-container" role="alert">
        {{ error }}
      </div>

      <p class="register-link">
        Don't have an account? 
        <router-link to="/register">Register here</router-link>
      </p>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/auth'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleSubmit = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const result = await authService.login(username.value, password.value)
    if (result.success) {
      router.push({ path: '/dashboard', replace: true })
    } else {
      error.value = result.error
      // Clear password on error
      password.value = ''
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@import './css/LoginForm.css';

.error-container {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  border-radius: 4px;
  color: #991b1b;
  font-size: 0.875rem;
  text-align: center;
}
</style>
