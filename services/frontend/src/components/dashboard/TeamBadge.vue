<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  teamName: string
}>()

// Pour l'instant, on extrait les 3 premières lettres pour faire un logo minimaliste style SaaS
const initials = computed(() => {
  return props.teamName.substring(0, 3).toUpperCase()
})
</script>

<template>
  <div class="flex flex-col items-center gap-3">
    <!-- Le container utilise le style liquid-glass avec un glow subtil au hover -->
    <div class="w-16 h-16 rounded-2xl liquid-glass flex items-center justify-center p-2 border border-sunset-secondary/30 liquid-glow-hover transition-all duration-300">
      <span class="text-2xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-sunset-accent">{{ initials }}</span>
    </div>
    <span class="text-sm font-semibold text-white/90 tracking-wide text-center">{{ teamName }}</span>
  </div>
</template>
