import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useAuthStore } from './stores/auth'
import { initTeamLogoSystem } from './utils/teamLogos'
import { applyDesignTokens } from './theme'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

applyDesignTokens()
initTeamLogoSystem()

const authStore = useAuthStore()
authStore.initAuth().finally(() => {
  app.mount('#app')
})
