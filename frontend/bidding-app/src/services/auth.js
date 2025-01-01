import axios from 'axios'

const API_URL = 'http://localhost:8000'

// Create an axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  validateStatus: status => status < 500
})

// Generic error messages that don't reveal system details
const ERROR_MESSAGES = {
  INVALID_CREDENTIALS: 'Invalid username or password',
  NETWORK_ERROR: 'Unable to connect to the service',
  VALIDATION_ERROR: 'Please check your input and try again',
  USER_EXISTS: 'Unable to create account with provided details',
  REGISTRATION_FAILED: 'Unable to complete registration',
  GENERAL_ERROR: 'An error occurred. Please try again'
}

class AuthService {
  constructor() {
    this.setupInterceptors()
  }

  setupInterceptors() {
    // Request interceptor for adding auth token
    api.interceptors.request.use(
      config => {
        const user = this.getCurrentUser()
        if (user?.token) {
          config.headers.Authorization = `${user.tokenType} ${user.token}`
        }
        return config
      },
      error => Promise.reject(error)
    )

    // Response interceptor for handling auth errors
    api.interceptors.response.use(
      response => response,
      error => {
        if (error.response?.status === 401) {
          this.logout()
        }
        return Promise.reject(error)
      }
    )
  }

  async login(username, password) {
    try {
      if (!username || !password) {
        return { 
          success: false, 
          error: ERROR_MESSAGES.VALIDATION_ERROR
        }
      }

      // Format data according to OAuth2PasswordRequestForm requirements
      const formData = new URLSearchParams()
      formData.append('username', username.trim())
      formData.append('password', password)
      formData.append('grant_type', 'password')
      formData.append('scope', '')
      formData.append('client_id', '')
      formData.append('client_secret', '')

      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })

      if (!response.data.access_token) {
        return { 
          success: false, 
          error: ERROR_MESSAGES.INVALID_CREDENTIALS
        }
      }

      // Store user data with token type for proper authorization header
      const userData = {
        token: response.data.access_token,
        tokenType: response.data.token_type,
        username: username.trim()
      }
      localStorage.setItem('user', JSON.stringify(userData))
      return { success: true }

    } catch (error) {
      if (!error.response) {
        return { 
          success: false, 
          error: ERROR_MESSAGES.NETWORK_ERROR
        }
      }

      return { 
        success: false, 
        error: ERROR_MESSAGES.INVALID_CREDENTIALS
      }
    }
  }

  async register(username, firstName, lastName, email, password) {
    try {
      if (!username || !firstName || !lastName || !email || !password) {
        return { 
          success: false, 
          error: ERROR_MESSAGES.VALIDATION_ERROR
        }
      }

      // Format data according to CreateUser schema requirements
      const data = {
        username: username.trim(),
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        password: password,
        confirm_password: password
      }

      const response = await api.post('/auth/signup', data, {
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.data && (response.data.id || response.data.username)) {
        return { success: true }
      }

      return { 
        success: false, 
        error: ERROR_MESSAGES.REGISTRATION_FAILED
      }

    } catch (error) {
      if (!error.response) {
        return { 
          success: false, 
          error: ERROR_MESSAGES.NETWORK_ERROR
        }
      }

      // Handle specific registration errors
      switch (error.response.status) {
        case 400:
          return {
            success: false,
            error: ERROR_MESSAGES.VALIDATION_ERROR
          }
        case 409:
          return {
            success: false,
            error: ERROR_MESSAGES.USER_EXISTS
          }
        default:
          return {
            success: false,
            error: ERROR_MESSAGES.REGISTRATION_FAILED
          }
      }
    }
  }

  logout() {
    localStorage.removeItem('user')
    window.location.href = '/login'
  }

  getCurrentUser() {
    try {
      const userStr = localStorage.getItem('user')
      return userStr ? JSON.parse(userStr) : null
    } catch (error) {
      this.logout()
      return null
    }
  }

  isAuthenticated() {
    const user = this.getCurrentUser()
    return !!user && !!user.token
  }
}

export const authService = new AuthService()
