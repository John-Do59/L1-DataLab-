<script setup lang="ts">
import TeamBadge from './TeamBadge.vue'
import ProbabilityBar from './ProbabilityBar.vue'

defineProps<{
  homeTeam: string
  awayTeam: string
  probH: number
  probD: number
  probA: number
  loading?: boolean
}>()
</script>

<template>
  <div class="relative w-full rounded-3xl p-[1px] liquid-glow group overflow-hidden">
    <!-- Glowing Border Gradient -->
    <div class="absolute inset-0 bg-gradient-to-br from-sunset-primary via-sunset-secondary to-sunset-accent opacity-60 group-hover:opacity-100 transition-opacity duration-700"></div>
    
    <!-- Content Core -->
    <div class="relative w-full h-full bg-[#010108]/90 backdrop-blur-2xl rounded-[23px] p-8 md:p-12 flex flex-col md:flex-row items-center justify-between gap-12 z-10">
      
      <!-- Internal Glow -->
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-sunset-secondary/10 blur-[100px] rounded-full pointer-events-none"></div>

      <!-- Loading State -->
      <div v-if="loading" class="absolute inset-0 z-20 flex flex-col items-center justify-center bg-[#010108]/60 backdrop-blur-md rounded-[23px]">
        <div class="w-12 h-12 border-4 border-sunset-primary/30 border-t-sunset-accent rounded-full animate-spin"></div>
        <span class="mt-4 text-sunset-accent font-medium tracking-widest text-sm animate-pulse">Running Neural Network...</span>
      </div>

      <!-- Teams Display -->
      <div class="flex-1 flex justify-center items-center gap-8 w-full">
        <TeamBadge :teamName="homeTeam" class="transform hover:scale-110 transition-transform duration-500" />
        <div class="text-sunset-accent font-black text-2xl tracking-widest opacity-80 mix-blend-screen">VS</div>
        <TeamBadge :teamName="awayTeam" class="transform hover:scale-110 transition-transform duration-500" />
      </div>

      <!-- Analytics & Probabilities -->
      <div class="flex-1 w-full flex flex-col justify-center">
        <h3 class="text-white text-xl font-bold mb-6 flex items-center gap-3">
          <span class="w-2 h-2 rounded-full bg-green-400 animate-pulse shadow-[0_0_10px_#4ade80]"></span>
          Live Prediction
        </h3>
        
        <ProbabilityBar 
          :probH="probH" 
          :probD="probD" 
          :probA="probA" 
          :homeLabel="homeTeam" 
          :awayLabel="awayTeam" 
        />
        
        <div class="mt-8 flex gap-4">
          <button class="px-6 py-3 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white text-sm font-medium transition-all backdrop-blur-md flex items-center gap-2">
            <span>View Deep Analysis</span>
            <span class="text-sunset-accent">→</span>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>
