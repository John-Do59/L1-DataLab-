<script setup lang="ts">
import { onMounted, ref } from 'vue'
import gsap from 'gsap'

const titleRef = ref(null)
const subtitleRef = ref(null)
const ctaRef = ref(null)

onMounted(() => {
  // Animation d'entrée GSAP ultra-smooth
  const tl = gsap.timeline({ defaults: { ease: "power4.out" } })
  
  tl.fromTo(titleRef.value, 
    { y: 50, opacity: 0, scale: 0.95 },
    { y: 0, opacity: 1, scale: 1, duration: 1.2, delay: 0.2 }
  )
  .fromTo(subtitleRef.value,
    { y: 30, opacity: 0 },
    { y: 0, opacity: 1, duration: 1 },
    "-=0.8"
  )
  .fromTo(ctaRef.value,
    { y: 20, opacity: 0 },
    { y: 0, opacity: 1, duration: 0.8 },
    "-=0.6"
  )
})
</script>

<template>
  <div class="min-h-[80vh] flex flex-col items-center justify-center text-center relative">
    
    <div class="max-w-4xl mx-auto space-y-8 relative z-10">
      
      <!-- Énorme Headline Typographique -->
      <h1 ref="titleRef" class="text-6xl md:text-8xl font-black tracking-tight text-white leading-tight opacity-0">
        Predict the future of <br/>
        <span class="text-gradient">Ligue 1</span>
      </h1>
      
      <!-- Sous-titre -->
      <p ref="subtitleRef" class="text-xl md:text-2xl text-sunset-secondary/80 font-medium max-w-2xl mx-auto opacity-0">
        Agentic Analytics as a Service. Explorez le championnat avec une précision algorithmique inédite et des insights générés par l'IA.
      </p>

      <!-- Call To Action (Liquidglass) -->
      <div ref="ctaRef" class="pt-8 opacity-0">
        <button class="group relative px-8 py-4 bg-sunset-primary text-white rounded-2xl font-semibold text-lg overflow-hidden transition-transform hover:scale-105 active:scale-95 shadow-[0_0_40px_-10px_#7232f2]">
          <!-- Effet de survol brillant -->
          <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300 ease-out rounded-2xl"></div>
          <span class="relative z-10 flex items-center gap-2">
            Start Exploring
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </span>
        </button>
      </div>

    </div>

    <!-- Data Elements Décoratifs (Floutés en arrière-plan) -->
    <div class="absolute top-[20%] left-[10%] liquid-glass p-6 rounded-2xl rotate-[-5deg] opacity-50 blur-sm">
      <div class="text-xs text-sunset-secondary">PSG Win Probability</div>
      <div class="text-2xl font-bold text-sunset-accent mt-1">78.4%</div>
    </div>

    <div class="absolute bottom-[20%] right-[10%] liquid-glass p-6 rounded-2xl rotate-[5deg] opacity-50 blur-sm">
      <div class="text-xs text-sunset-secondary">OM Elo Rating</div>
      <div class="text-2xl font-bold text-sunset-accent mt-1">1650.2</div>
      <div class="text-xs text-green-400 mt-1">▲ +12 pts</div>
    </div>

  </div>
</template>
