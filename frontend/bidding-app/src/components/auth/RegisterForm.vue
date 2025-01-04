<template>
  <div class="register-container">
    <form @submit.prevent="handleSubmit" class="register-form">
      <h1 class="title">BidFlow</h1>
      
      <div class="form-groups">
        <div class="form-group">
          <input
            type="text"
            v-model="username"
            placeholder="Username"
            required
            minlength="3"
          />
        </div>

        <div class="name-group">
          <div class="form-group half">
            <input
              type="text"
              v-model="firstName"
              placeholder="First Name"
              required
            />
          </div>
          <div class="form-group half">
            <input
              type="text"
              v-model="lastName"
              placeholder="Last Name"
              required
            />
          </div>
        </div>

        <div class="form-group">
          <input
            type="email"
            v-model="email"
            placeholder="Email"
            required
          />
        </div>

        <div class="password-field">
          <input :type="showPassword ? 'text' : 'password'" v-model="password" placeholder="Password" required minlength="8" />
          <button type="button" class="toggle-password" @click="togglePasswordVisibility" :aria-label="showPassword ? 'Hide password' : 'Show password'">
            <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
              <line x1="1" y1="1" x2="23" y2="23"></line>
            </svg>
          </button>
        </div>

        <div class="password-field">
          <input :type="showConfirmPassword ? 'text' : 'password'" v-model="confirmPassword" placeholder="Confirm Password" required minlength="8" />
          <button type="button" class="toggle-password" @click="toggleConfirmPasswordVisibility" :aria-label="showConfirmPassword ? 'Hide password' : 'Show password'">
            <svg v-if="!showConfirmPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
              <line x1="1" y1="1" x2="23" y2="23"></line>
            </svg>
          </button>
        </div>
      </div>

      <div class="form-footer">
        <button type="submit" :disabled="loading" class="submit-btn">
          {{ loading ? 'Creating Account...' : 'Register' }}
        </button>

        <div v-if="error" class="error-container" role="alert">
          {{ error }}
        </div>

        <p v-if="successMessage" class="success-message">{{ successMessage }}</p>

        <div v-if="successMessage" class="success-container" role="status">
          {{ successMessage }}
        </div>

        <p class="login-link">
          Already have an account? 
          <router-link to="/login">Login here</router-link>
        </p>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authService } from '@/services/auth'

const router = useRouter()
const username = ref('')
const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const successMessage = ref('')
const loading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const toggleConfirmPasswordVisibility = () => {
  showConfirmPassword.value = !showConfirmPassword.value
}

const handleSubmit = async () => {
  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  loading.value = true
  error.value = ''
  successMessage.value = ''
  
  try {
    const result = await authService.register(
      username.value,
      firstName.value,
      lastName.value, 
      email.value,
      password.value
    )
    
    if (result.success) {
      successMessage.value = 'Account created successfully! Redirecting to login...'
      // Clear form
      username.value = ''
      firstName.value = ''
      lastName.value = ''
      email.value = ''
      password.value = ''
      confirmPassword.value = ''
      // Redirect after a short delay to show the success message
      setTimeout(() => {
        router.push({ path: '/login', replace: true })
      }, 2000)
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

<style scoped>
@import './css/RegisterForm.css';

.form-groups {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.name-group {
  display: flex;
  gap: 1rem;
}

.half {
  flex: 1;
  margin-bottom: 0;
}

.form-footer {
  margin-top: auto;
}

.error-container {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #fee2e2;
  border: 1px solid #ef4444;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.875rem;
  text-align: center;
}

.success-container {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #dcfce7;
  border: 1px solid #22c55e;
  border-radius: 8px;
  color: #166534;
  font-size: 0.875rem;
  text-align: center;
  animation: fadeIn 0.3s ease-in;
}

.success-message {
  color: green;
  margin-top: 10px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Override some base styles for better spacing */
.register-form {
  gap: 2rem;
  padding: 2.5rem;
}

.form-group {
  margin-bottom: 0;
}

.password-field {
  position: relative;
}

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #4cffd6;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease;
}

.toggle-password:hover {
  color: #3bbfbf;
}

.toggle-password svg {
  display: block;
}

input {
  transition: all 0.2s ease;
}

input:focus {
  transform: translateY(-1px);
}

.submit-btn {
  margin-top: 0;
}
</style>
