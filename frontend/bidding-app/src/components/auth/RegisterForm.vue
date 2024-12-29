<template>
  <div class="register-container">
    <form @submit.prevent="handleSubmit" class="register-form">
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

      <div class="form-group">
        <input
          type="password"
          v-model="confirmPassword"
          placeholder="Confirm Password"
          required
        />
      </div>

      <button type="submit" :disabled="loading" class="submit-btn">
        {{ loading ? 'Creating Account...' : 'Register' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>

      <p class="login-link">
        Already have an account? 
        <router-link to="/login">Login here</router-link>
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
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

const handleSubmit = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  loading.value = true
  error.value = ''
  
  try {
    const result = await authService.register(
      username.value, 
      email.value, 
      password.value
    )
    
    if (result.success) {
      router.push('/login')
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
@import './css/RegisterForm.css';
</style>
