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

// Intercepteur pour gérer les erreurs d'authentification
api.interceptors.response.use((response) => response, (error) => {
  if (error.response && error.response.status === 401) {
    // Si le token est invalide ou expiré, on purge et on redirige
    localStorage.removeItem('access_token')
    window.location.href = '/login'
  }
  return Promise.reject(error)
})

export default api
