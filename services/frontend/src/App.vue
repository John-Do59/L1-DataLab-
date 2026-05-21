<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen relative overflow-hidden bg-sunset-bg">
    
    <!-- Background Glows (Ambiance Apple / Leonardo.ai) -->
    <div class="fixed top-[-10%] left-[-10%] w-[50%] h-[50%] rounded-full bg-sunset-primary/20 blur-[120px] pointer-events-none"></div>
    <div class="fixed bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-sunset-secondary/15 blur-[100px] pointer-events-none"></div>

    <!-- Navigation Liquidglass -->
    <header class="fixed top-0 left-0 w-full z-50 px-6 py-4">
      <nav class="max-w-7xl mx-auto liquid-glass rounded-2xl px-6 py-3 flex justify-between items-center liquid-glow">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded-lg bg-gradient-to-tr from-sunset-primary to-sunset-secondary flex items-center justify-center">
            <span class="text-white font-bold text-sm">L1</span>
          </div>
          <span class="font-semibold text-sunset-accent tracking-wide text-lg">DataLab</span>
        </div>
        
        <div class="flex gap-6 text-sm font-medium text-sunset-secondary/80">
          <RouterLink to="/" class="hover:text-sunset-accent transition-colors">Home</RouterLink>
          <RouterLink to="/pricing" class="hover:text-sunset-accent transition-colors">Tarifs</RouterLink>
          <RouterLink to="/prediction" class="hover:text-sunset-accent transition-colors">Predictions</RouterLink>
          <RouterLink to="/ai-insights" class="hover:text-sunset-accent transition-colors">AI Insights</RouterLink>
          <RouterLink to="/history" class="hover:text-sunset-accent transition-colors">Historique</RouterLink>
        </div>

        <div class="flex items-center">
          <RouterLink to="/login" class="liquid-glass hover:bg-sunset-primary/20 px-4 py-2 rounded-xl text-sunset-accent transition-all duration-300 text-sm font-medium border border-sunset-secondary/30">
            Sign In / Dashboard
          </RouterLink>
        </div>
      </nav>
    </header>

    <!-- Page Content -->
    <main class="relative z-10 pt-32 px-6">
      <RouterView />
    </main>

  </div>
</template>

<style>
/* Transitions de page globales (Vue Router) */
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
