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
    class="absolute rounded-3xl flex items-center justify-center liquid-glass p-4 border border-sunset-primary/30 shadow-[0_0_30px_-5px_rgba(200,118,255,0.2)] transition-all duration-700 hover:scale-110 hover:shadow-[0_0_50px_-5px_rgba(246,179,229,0.5)] hover:border-sunset-accent cursor-default backdrop-blur-xl bg-[#010108]/40"
    :class="sizeClasses"
    :style="animationStyle"
  >
    <img v-if="imgSrc" :src="imgSrc" :alt="name" class="w-full h-full object-contain drop-shadow-[0_0_15px_rgba(255,255,255,0.3)] transition-transform duration-500 hover:scale-110" />
    <span v-else class="font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-sunset-accent opacity-90 tracking-tighter">{{ initials }}</span>
  </div>
</template>

<style scoped>
@keyframes float {
  0% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(2deg); }
  100% { transform: translateY(0px) rotate(0deg); }
}
</style>
