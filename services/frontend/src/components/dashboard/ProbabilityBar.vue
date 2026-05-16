<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  probH: number
  probD?: number
  probA: number
  homeLabel?: string
  awayLabel?: string
}>()

const hPercent = computed(() => Math.round(props.probH * 100))
const dPercent = computed(() => props.probD ? Math.round(props.probD * 100) : 0)
const aPercent = computed(() => Math.round(props.probA * 100))
</script>

<template>
  <div class="w-full">
    <div class="flex justify-between text-[11px] uppercase tracking-wider mb-2 font-medium text-sunset-accent/80">
      <span class="flex items-center gap-1"><div class="w-2 h-2 rounded-full bg-sunset-primary"></div> {{ homeLabel || 'Home' }} ({{ hPercent }}%)</span>
      <span v-if="probD" class="flex items-center gap-1"><div class="w-2 h-2 rounded-full bg-sunset-secondary"></div> Draw ({{ dPercent }}%)</span>
      <span class="flex items-center gap-1"><div class="w-2 h-2 rounded-full bg-sunset-accent"></div> {{ awayLabel || 'Away' }} ({{ aPercent }}%)</span>
    </div>
    
    <div class="flex h-1.5 w-full rounded-full overflow-hidden bg-sunset-bg/80 border border-sunset-primary/10 shadow-inner">
      <div 
        class="bg-gradient-to-r from-sunset-primary/80 to-sunset-primary h-full transition-all duration-1000 ease-out" 
        :style="{ width: `${hPercent}%` }"
      ></div>
      
      <div 
        v-if="probD" 
        class="bg-gradient-to-r from-sunset-secondary/80 to-sunset-secondary h-full transition-all duration-1000 ease-out border-l border-r border-sunset-bg/50" 
        :style="{ width: `${dPercent}%` }"
      ></div>
      
      <div 
        class="bg-gradient-to-r from-sunset-accent/80 to-sunset-accent h-full transition-all duration-1000 ease-out" 
        :style="{ width: `${aPercent}%` }"
      ></div>
    </div>
  </div>
</template>
