import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/axios'

interface User {
  id: number
  username: string
  email: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username: string, password: string) {
    // FastAPI OAuth2 requiert un form-urlencoded
    const params = new URLSearchParams()
    params.append('username', username)
    params.append('password', password)

    try {
      const response = await api.post('/auth/login', params, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      token.value = response.data.access_token
      localStorage.setItem('access_token', token.value!)
      await fetchUser()
      return true
    } catch (error) {
      console.error("Login failed", error)
      throw error
    }
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const response = await api.get('/users/me')
      user.value = response.data
    } catch (error) {
      logout()
    }
  }

  async function register(username: string, email: string, password: string) {
    try {
      const response = await api.post('/users', {
        username,
        email,
        password
      })
      // Si la création réussit, on connecte l'utilisateur dans la foulée
      await login(username, password)
      return true
    } catch (error) {
      console.error("Registration failed", error)
      throw error
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
  }

  async function initAuth() {
    if (token.value && !user.value) {
      await fetchUser()
    }
  }

  return { token, user, isAuthenticated, login, logout, fetchUser, register, initAuth }
})
