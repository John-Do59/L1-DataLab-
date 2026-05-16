<script setup lang="ts">
import ProbabilityBar from './ProbabilityBar.vue'

defineProps<{
  homeTeam: string
  awayTeam: string
  date: string
  status: string
  prediction?: { probH: number, probD: number, probA: number }
}>()
</script>

<template>
  <div class="liquid-glass rounded-2xl p-6 border border-sunset-primary/10 hover:border-sunset-secondary/40 transition-all duration-500 liquid-glow-hover cursor-pointer group h-full flex flex-col justify-between relative overflow-hidden">
    
    <!-- Subtle background pattern on hover -->
    <div class="absolute inset-0 bg-gradient-to-br from-sunset-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>

    <div class="flex justify-between items-center mb-6 relative z-10">
      <span class="text-[10px] text-sunset-accent/60 uppercase tracking-widest font-bold">{{ date }}</span>
      <span class="text-[10px] px-2 py-1 rounded-md bg-sunset-primary/10 text-sunset-primary border border-sunset-primary/20 uppercase tracking-wide">{{ status }}</span>
    </div>
    
    <div class="flex justify-between items-center gap-4 relative z-10">
      <div class="flex flex-col items-start gap-1">
        <span class="text-white font-medium text-lg">{{ homeTeam }}</span>
      </div>
      <span class="text-sunset-secondary/40 font-black text-sm italic">vs</span>
      <div class="flex flex-col items-end gap-1">
        <span class="text-white font-medium text-lg">{{ awayTeam }}</span>
      </div>
    </div>
    
    <div class="mt-8 relative z-10 min-h-[32px]">
      <div v-if="prediction" class="opacity-80 group-hover:opacity-100 transition-opacity duration-300">
        <ProbabilityBar :probH="prediction.probH" :probD="prediction.probD" :probA="prediction.probA" />
      </div>
      <div v-else class="flex items-center justify-center h-full">
        <button class="text-xs text-sunset-accent/80 hover:text-sunset-accent transition-colors flex items-center gap-2 group/btn">
          <span class="w-4 h-4 rounded-full border border-sunset-accent/50 flex items-center justify-center group-hover/btn:bg-sunset-accent/20 transition-colors">+</span>
          Run Prediction
        </button>
      </div>
    </div>
  </div>
</template>
