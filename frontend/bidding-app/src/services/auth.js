import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

class AuthService {
  async login(username, password) {
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        username,
        password
      })
      
      if (response.data.token) {
        localStorage.setItem('user', JSON.stringify(response.data))
        return { success: true }
      }
      
      return {
        success: false,
        error: 'Invalid credentials'
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to login'
      }
    }
  }

  async register(username, email, password) {
    try {
      const response = await axios.post(`${API_URL}/auth/register`, {
        username,
        email,
        password
      })
      
      if (response.data.id) {
        return { success: true }
      }
      
      return {
        success: false,
        error: 'Registration failed'
      }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.message || 'Failed to register'
      }
    }
  }

  logout() {
    localStorage.removeItem('user')
  }

  getCurrentUser() {
    const userStr = localStorage.getItem('user')
    if (!userStr) return null
    return JSON.parse(userStr)
  }

  isAuthenticated() {
    const user = this.getCurrentUser()
    return !!user && !!user.token
  }
}

export const authService = new AuthService()
