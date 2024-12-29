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

  logout() {
    localStorage.removeItem('user')
  }

  getCurrentUser() {
    const userStr = localStorage.getItem('user')
    if (!userStr) return null
    return JSON.parse(userStr)
  }
}

export const authService = new AuthService()
