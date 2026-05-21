<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterView, RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const userMenuOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)

const handleLogout = () => {
  userMenuOpen.value = false
  authStore.logout()
  router.push({ name: 'login' })
}

const closeMenuOnClickOutside = (e: MouseEvent) => {
  if (menuRef.value && !menuRef.value.contains(e.target as Node)) {
    userMenuOpen.value = false
  }
}

onMounted(async () => {
  await authStore.initAuth()
  document.addEventListener('click', closeMenuOnClickOutside)
})
onUnmounted(() => document.removeEventListener('click', closeMenuOnClickOutside))
</script>

<template>
  <div class="min-h-screen relative overflow-hidden bg-sunset-bg">
    
    <!-- Background Glows -->
    <div class="fixed top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-sunset-primary/20 blur-[120px] pointer-events-none"></div>
    <div class="fixed bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-sunset-secondary/15 blur-[100px] pointer-events-none"></div>

    <header class="fixed top-0 left-0 w-full z-50 px-6 py-4">
      <nav class="max-w-7xl mx-auto liquid-glass rounded-2xl px-6 py-3 flex justify-between items-center liquid-glow gap-4">
        <RouterLink to="/" class="flex items-center gap-2 shrink-0">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-sunset-primary to-sunset-secondary flex items-center justify-center">
            <span class="text-white font-bold text-sm">L1</span>
          </div>
          <span class="font-semibold text-sunset-accent tracking-wide text-lg">DataLab</span>
        </RouterLink>
        
        <div class="hidden md:flex gap-6 text-sm font-medium text-sunset-secondary/80">
          <RouterLink to="/" class="hover:text-sunset-accent transition-colors">Home</RouterLink>
          <RouterLink to="/pricing" class="hover:text-sunset-accent transition-colors">Tarifs</RouterLink>
          <template v-if="authStore.isAuthenticated">
            <RouterLink to="/dashboard" class="hover:text-sunset-accent transition-colors">Dashboard</RouterLink>
            <RouterLink to="/prediction" class="hover:text-sunset-accent transition-colors">Predictions</RouterLink>
            <RouterLink to="/rag" class="hover:text-sunset-accent transition-colors">RAG Agent</RouterLink>
            <RouterLink to="/ai-insights" class="hover:text-sunset-accent transition-colors">AI Insights</RouterLink>
            <RouterLink to="/history" class="hover:text-sunset-accent transition-colors">Historique</RouterLink>
          </template>
        </div>

        <div class="flex items-center gap-3 shrink-0">
          <template v-if="authStore.isAuthenticated">
            <div ref="menuRef" class="relative">
              <button
                type="button"
                @click.stop="userMenuOpen = !userMenuOpen"
                class="liquid-glass flex items-center gap-2 px-4 py-2 rounded-xl text-sunset-accent text-sm font-medium border border-sunset-secondary/30 hover:bg-sunset-primary/20 transition-all"
              >
                <span class="w-7 h-7 rounded-lg bg-gradient-to-tr from-sunset-primary/80 to-sunset-secondary/80 flex items-center justify-center text-xs font-bold text-white">
                  {{ (authStore.user?.username || 'U').charAt(0).toUpperCase() }}
                </span>
                <span class="hidden sm:inline max-w-[120px] truncate">{{ authStore.user?.username || 'Compte' }}</span>
                <span class="text-sunset-secondary/60 text-xs">▾</span>
              </button>
              <div
                v-if="userMenuOpen"
                class="absolute right-0 mt-2 w-52 liquid-glass-strong rounded-xl border border-sunset-primary/30 py-2 shadow-xl z-[60]"
              >
                <RouterLink
                  to="/profile"
                  class="block px-4 py-2.5 text-sm text-sunset-secondary hover:text-sunset-accent hover:bg-sunset-primary/10 transition-colors"
                  @click="userMenuOpen = false"
                >
                  Mon profil
                </RouterLink>
                <RouterLink
                  to="/dashboard"
                  class="block px-4 py-2.5 text-sm text-sunset-secondary hover:text-sunset-accent hover:bg-sunset-primary/10 transition-colors"
                  @click="userMenuOpen = false"
                >
                  Command Center
                </RouterLink>
                <hr class="my-1 border-sunset-primary/20" />
                <button
                  type="button"
                  @click="handleLogout"
                  class="w-full text-left px-4 py-2.5 text-sm text-red-300/90 hover:bg-red-500/10 transition-colors"
                >
                  Se déconnecter
                </button>
              </div>
            </div>
          </template>
          <template v-else>
            <RouterLink
              to="/login"
              class="liquid-glass hover:bg-sunset-primary/20 px-4 py-2 rounded-xl text-sunset-accent transition-all text-sm font-medium border border-sunset-secondary/30"
            >
              Connexion
            </RouterLink>
            <RouterLink
              to="/register"
              class="bg-gradient-to-r from-sunset-primary to-sunset-secondary px-4 py-2 rounded-xl text-white text-sm font-semibold hover:shadow-[0_0_20px_-5px_#c876ff] transition-all"
            >
              S'inscrire
            </RouterLink>
          </template>
        </div>
      </nav>
    </header>

    <main class="relative z-10 pt-32 px-6">
      <RouterView />
    </main>

  </div>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
