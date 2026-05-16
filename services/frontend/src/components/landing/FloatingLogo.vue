<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  name: string
  imgSrc?: string
  delay?: number
  duration?: number
  size?: 'sm' | 'md' | 'lg'
}>()

const initials = computed(() => props.name.substring(0, 3).toUpperCase())
const animationStyle = computed(() => ({
  animation: `float ${props.duration || 6}s ease-in-out infinite`,
  animationDelay: `${props.delay || 0}s`
}))

const sizeClasses = computed(() => {
  switch(props.size) {
    case 'sm': return 'w-12 h-12 text-sm'
    case 'lg': return 'w-24 h-24 text-3xl'
    default: return 'w-16 h-16 text-xl'
  }
})
</script>

<template>
  <div 
    class="absolute flex items-center justify-center transition-all duration-700 hover:scale-110 cursor-default"
    :class="sizeClasses"
    :style="animationStyle"
  >
    <!-- Le double drop-shadow crée un contour de 1px précis + un glow diffus -->
    <img 
      v-if="imgSrc" 
      :src="imgSrc" 
      :alt="name" 
      class="w-full h-full object-contain drop-shadow-[0_0_1px_rgba(255,255,255,0.6)] drop-shadow-[0_0_15px_rgba(200,118,255,0.3)] transition-all duration-500 hover:scale-110 hover:drop-shadow-[0_0_2px_rgba(255,255,255,0.9)] hover:drop-shadow-[0_0_25px_rgba(246,179,229,0.7)]" 
    />
    <span v-else class="font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-sunset-accent opacity-90 tracking-tighter drop-shadow-[0_0_10px_rgba(200,118,255,0.5)]">{{ initials }}</span>
  </div>
</template>

<style scoped>
@keyframes float {
  0% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(2deg); }
  100% { transform: translateY(0px) rotate(0deg); }
}
</style>
