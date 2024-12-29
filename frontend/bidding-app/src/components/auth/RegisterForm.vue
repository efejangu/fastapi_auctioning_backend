<template>
  <div class="register-container">
    <form @submit.prevent="handleSubmit" class="register-form">
      <h1 class="title">BidFlow</h1>
      <div class="form-group">
        <label for="username">Username</label>
        <input
          type="text"
          id="username"
          v-model="username"
          required
          placeholder="Choose a username"
        />
      </div>

      <div class="form-group">
        <label for="email">Email</label>
        <input
          type="email"
          id="email"
          v-model="email"
          required
          placeholder="Enter your email"
        />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input
          type="password"
          id="password"
          v-model="password"
          required
          placeholder="Choose a password"
        />
      </div>

      <div class="form-group">
        <label for="confirmPassword">Confirm Password</label>
        <input
          type="password"
          id="confirmPassword"
          v-model="confirmPassword"
          required
          placeholder="Confirm your password"
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
    // TODO: Implement registration logic
    console.log('Register attempt:', {
      username: username.value,
      email: email.value,
      password: password.value
    })
    router.push('/login')
  } catch (err) {
    error.value = err.message || 'Failed to register'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 1rem;
}

.register-form {
  background: var(--card-bg);
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 400px;
  border: 1px solid var(--border-color);
}

.title {
  text-align: center;
  margin-bottom: 2rem;
  font-family: 'Dancing Script', cursive;
  font-size: 2.5rem;
  background: linear-gradient(45deg, #ffffff, #64ffda);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-light);
  font-weight: 500;
}

input {
  width: 100%;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 1rem;
  background-color: var(--bg-darker);
  color: var(--text-light);
  border: 1px solid var(--border-color);
  transition: all 0.3s ease;
}

input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(66, 185, 131, 0.1);
}

.submit-btn {
  width: 100%;
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 1rem;
  margin-top: 1.5rem;
  background: linear-gradient(45deg, var(--primary-color), #64ffda);
  color: var(--bg-darker);
  font-weight: bold;
  transition: transform 0.2s;
}

.submit-btn:hover {
  transform: translateY(-1px);
}

.submit-btn:disabled {
  background: var(--text-gray);
  transform: none;
  color: var(--bg-darker);
  opacity: 0.7;
}

.error {
  color: #ff6b6b;
  margin-top: 1rem;
  text-align: center;
  font-size: 0.9rem;
  font-weight: 500;
}

.login-link {
  text-align: center;
  margin-top: 1.5rem;
  color: var(--text-light);
}

.login-link a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: bold;
}

.login-link a:hover {
  text-decoration: underline;
}
</style>
