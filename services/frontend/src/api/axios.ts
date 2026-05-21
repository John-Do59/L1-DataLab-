import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8002',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Intercepteur pour injecter le token JWT automatiquement
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

// Intercepteur : redirection uniquement si une session existante expire
api.interceptors.response.use((response) => response, (error) => {
  if (error.response?.status === 401) {
    const hadToken = !!localStorage.getItem('access_token')
    localStorage.removeItem('access_token')
    const onAuthPage = /^\/(login|register)$/.test(window.location.pathname)
    if (hadToken && !onAuthPage) {
      window.location.href = '/login'
    }
  }
  return Promise.reject(error)
})

export default api
