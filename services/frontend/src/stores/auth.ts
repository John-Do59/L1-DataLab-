import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/axios'
import type { SubscriptionTier } from '../features/pricing/plans'

const TIER_STORAGE_KEY = 'subscription_tier'

function readStoredTier(): SubscriptionTier {
  const raw = localStorage.getItem(TIER_STORAGE_KEY)
  if (raw === 'pro' || raw === 'max' || raw === 'free') return raw
  return 'free'
}

interface User {
  id: number
  username: string
  email: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<User | null>(null)
  const subscriptionTier = ref<SubscriptionTier>(readStoredTier())

  const isAuthenticated = computed(() => !!token.value)

  function setSubscriptionTier(tier: SubscriptionTier) {
    subscriptionTier.value = tier
    localStorage.setItem(TIER_STORAGE_KEY, tier)
  }

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
    subscriptionTier.value = 'free'
    localStorage.removeItem('access_token')
    localStorage.removeItem(TIER_STORAGE_KEY)
  }

  async function initAuth() {
    if (token.value && !user.value) {
      await fetchUser()
    }
  }

  return {
    token,
    user,
    subscriptionTier,
    isAuthenticated,
    login,
    logout,
    fetchUser,
    register,
    initAuth,
    setSubscriptionTier,
  }
})
