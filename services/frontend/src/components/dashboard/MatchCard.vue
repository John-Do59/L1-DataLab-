<script setup lang="ts">
import { computed } from 'vue'
import ProbabilityBar from './ProbabilityBar.vue'
import { getTeamVisuals } from '../../utils/teamVisuals'

const props = defineProps<{
  homeTeam: string
  awayTeam: string
  homeLogo?: string
  awayLogo?: string
  date: string
  status: string
  homeScore?: number | null
  awayScore?: number | null
  prediction?: { probH: number, probD: number, probA: number }
}>()

const homeVisuals = computed(() => getTeamVisuals(props.homeTeam))
const awayVisuals = computed(() => getTeamVisuals(props.awayTeam))
const cardStyle = computed(() => ({
  ...(homeVisuals.value?.cssVars ?? {}),
  ...(awayVisuals.value
    ? { '--tv-away-primary': awayVisuals.value.primary }
    : {}),
}))
</script>

<template>
  <div
    class="liquid-glass rounded-2xl p-6 border transition-all duration-500 liquid-glow-hover cursor-pointer group h-full flex flex-col justify-between relative overflow-hidden"
    :style="[
      cardStyle,
      {
        borderColor: homeVisuals ? 'var(--tv-border)' : undefined,
        boxShadow: homeVisuals ? '0 0 28px var(--tv-glow)' : undefined,
      },
    ]"
    :class="!homeVisuals ? 'border-sunset-primary/10 hover:border-sunset-secondary/40' : ''"
  >
    
    <!-- Subtle background pattern on hover -->
    <div class="absolute inset-0 bg-gradient-to-br from-sunset-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>

    <div class="flex justify-between items-center mb-6 relative z-10">
      <span class="text-[10px] text-sunset-accent/60 uppercase tracking-widest font-bold">{{ date }}</span>
      <span class="text-[10px] px-2 py-1 rounded-md bg-sunset-primary/10 text-sunset-primary border border-sunset-primary/20 uppercase tracking-wide">{{ status }}</span>
    </div>
    
    <div class="flex justify-between items-center gap-2 relative z-10">
      <div class="flex flex-col items-center gap-2 w-1/3">
        <img
          v-if="homeLogo"
          :src="homeLogo"
          class="w-10 h-10 object-contain"
          :style="homeVisuals ? { filter: homeVisuals.glowFilter } : undefined"
        />
        <span
          class="font-medium text-xs text-center leading-tight"
          :style="homeVisuals ? { color: homeVisuals.primary } : { color: 'white' }"
        >{{ homeTeam }}</span>
      </div>
      
      <div class="w-1/3 flex justify-center">
        <div v-if="homeScore !== undefined && awayScore !== undefined && homeScore !== null && awayScore !== null" class="flex items-center gap-2 px-3 py-1 bg-white/5 rounded-lg border border-white/10">
          <span class="text-lg font-bold text-white">{{ homeScore }}</span>
          <span class="text-sunset-accent/50">-</span>
          <span class="text-lg font-bold text-white">{{ awayScore }}</span>
        </div>
        <span v-else class="text-sunset-secondary/40 font-black text-sm italic">vs</span>
      </div>
      
      <div class="flex flex-col items-center gap-2 w-1/3">
        <img
          v-if="awayLogo"
          :src="awayLogo"
          class="w-10 h-10 object-contain"
          :style="awayVisuals ? { filter: awayVisuals.glowFilter } : undefined"
        />
        <span
          class="font-medium text-xs text-center leading-tight"
          :style="awayVisuals ? { color: awayVisuals.primary } : { color: 'white' }"
        >{{ awayTeam }}</span>
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
