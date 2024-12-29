<template>
  <div class="login-container">
    <form @submit.prevent="handleSubmit" class="login-form">
      <h1 class="title">BidFlow</h1>
      <div class="form-group">
        <input
          type="email"
          v-model="email"
          placeholder="Email"
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
        {{ loading ? 'Loading...' : 'Login' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>

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
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleSubmit = async () => {
  loading.value = true
  error.value = ''
  
  try {
    const result = await authService.login(email.value, password.value)
    
    if (result.success) {
      router.push('/dashboard')
    } else {
      error.value = result.error
    }
  } catch (err) {
    error.value = 'An unexpected error occurred'
  } finally {
    loading.value = false
  }
}
</script>

<style>
@import './css/LoginForm.css';
</style>
