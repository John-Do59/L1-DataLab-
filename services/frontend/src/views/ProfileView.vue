<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import bgStadium2 from '../assets/backgrounds/bg_stadium_2.jpg'

const router = useRouter()
const authStore = useAuthStore()

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUser()
  }
})

const handleLogout = () => {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="fixed inset-0 z-[-1] pointer-events-none bg-[#010108]">
    <img :src="bgStadium2" alt="Stadium Background" class="w-full h-full object-cover opacity-70" />
    <div class="absolute inset-0 bg-gradient-to-t from-[#010108]/90 via-[#010108]/40 to-transparent"></div>
  </div>

  <div class="max-w-2xl mx-auto pb-16 relative z-10">
    <div class="mb-8">
      <p class="text-xs font-bold tracking-[0.25em] uppercase text-sunset-primary mb-2">Espace analyste</p>
      <h1 class="text-3xl md:text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white via-sunset-accent to-sunset-secondary">
        Mon profil
      </h1>
      <p class="text-sunset-secondary/80 mt-2 font-light">
        Compte L1 DataLab — accès aux prédictions, historique et insights IA.
      </p>
    </div>

    <div class="liquid-glass-strong rounded-3xl p-8 liquid-glow border border-sunset-primary/30 space-y-6">
      <div class="flex items-center gap-4 pb-6 border-b border-sunset-primary/20">
        <div class="w-16 h-16 rounded-2xl bg-gradient-to-tr from-sunset-primary to-sunset-secondary flex items-center justify-center text-2xl font-black text-white shadow-[0_0_30px_rgba(114,50,242,0.4)]">
          {{ (authStore.user?.username || '?').charAt(0).toUpperCase() }}
        </div>
        <div>
          <h2 class="text-xl font-bold text-white">{{ authStore.user?.username || '—' }}</h2>
          <p class="text-sunset-secondary text-sm">{{ authStore.user?.email || 'Chargement…' }}</p>
        </div>
      </div>

      <dl class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
        <div class="bg-sunset-bg/40 rounded-xl p-4 border border-sunset-primary/20">
          <dt class="text-sunset-secondary/70 uppercase tracking-wider text-xs mb-1">Identifiant</dt>
          <dd class="text-white font-mono">#{{ authStore.user?.id ?? '—' }}</dd>
        </div>
        <div class="bg-sunset-bg/40 rounded-xl p-4 border border-sunset-primary/20">
          <dt class="text-sunset-secondary/70 uppercase tracking-wider text-xs mb-1">Plan</dt>
          <dd class="text-sunset-accent font-semibold">Analyst Pro (cert)</dd>
        </div>
      </dl>

      <div class="flex flex-wrap gap-3 pt-2">
        <button
          type="button"
          @click="router.push('/prediction')"
          class="px-5 py-2.5 bg-gradient-to-r from-sunset-primary to-sunset-secondary text-white font-semibold rounded-xl hover:shadow-[0_0_20px_-5px_#c876ff] transition-all"
        >
          Nouvelle prédiction
        </button>
        <button
          type="button"
          @click="router.push('/history')"
          class="px-5 py-2.5 liquid-glass text-sunset-accent font-medium rounded-xl border border-sunset-secondary/30 hover:bg-sunset-primary/20 transition-all"
        >
          Voir l'historique
        </button>
        <button
          type="button"
          @click="router.push('/ai-insights')"
          class="px-5 py-2.5 liquid-glass text-sunset-secondary font-medium rounded-xl border border-white/10 hover:text-sunset-accent transition-all"
        >
          AI Insights (MLOps)
        </button>
      </div>

      <button
        type="button"
        @click="handleLogout"
        class="w-full py-3 rounded-xl border border-red-400/30 text-red-300/90 hover:bg-red-500/10 transition-colors text-sm font-medium"
      >
        Se déconnecter
      </button>
    </div>
  </div>
</template>
