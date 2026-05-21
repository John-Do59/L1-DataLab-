<script setup lang="ts">
import RagEntity from '../../../components/rag/RagEntity.vue'
import type { PricingCtaAction } from '../composables/usePricingCta'

defineProps<{
  actions: PricingCtaAction[]
}>()
</script>

<template>
  <section class="relative min-h-[70vh] flex flex-col items-center justify-center text-center px-4 py-16 overflow-hidden">
    <div
      class="absolute inset-0 pointer-events-none"
      aria-hidden="true"
      style="background: radial-gradient(ellipse 80% 60% at 50% 20%, rgba(114, 50, 242, 0.35), transparent 55%),
        radial-gradient(ellipse 50% 40% at 80% 60%, rgba(200, 118, 255, 0.2), transparent 50%),
        radial-gradient(ellipse 40% 35% at 15% 70%, rgba(34, 211, 238, 0.12), transparent 45%)"
    />
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[min(90vw,520px)] h-[min(90vw,520px)] rounded-full bg-sunset-primary/20 blur-[100px] pointer-events-none animate-pulse-slow" />

    <div class="relative z-10 mb-8 scale-90 md:scale-100">
      <RagEntity state="idle" :showStatus="false" />
    </div>

    <p class="relative z-10 text-[10px] md:text-xs font-bold tracking-[0.35em] uppercase text-sunset-primary mb-3">
      L1 DataLab · Agentic Analytics
    </p>
    <h1
      class="relative z-10 text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-black max-w-4xl leading-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-sunset-accent to-sunset-secondary drop-shadow-[0_0_40px_rgba(200,118,255,0.25)]"
    >
      Unlock the Full Power of the AI Football Oracle
    </h1>
    <p class="relative z-10 mt-5 text-sm md:text-base text-sunset-secondary/85 max-w-2xl font-light leading-relaxed">
      Plateforme IA sportive premium — prédictions neuronales, Oracle RAG, mémoire contextuelle et analytics Ligue 1.
      Choisissez le plan qui correspond à votre intensité d’analyse.
    </p>

    <div class="relative z-10 mt-10 flex flex-wrap items-center justify-center gap-3">
      <button
        v-for="action in actions"
        :key="action.id"
        type="button"
        :disabled="action.disabled"
        class="px-6 py-3 rounded-xl text-sm font-semibold transition-all duration-300 min-w-[160px]"
        :class="{
          'bg-gradient-to-r from-sunset-primary to-sunset-secondary text-white hover:shadow-[0_0_30px_-5px_#c876ff] hover:scale-[1.02]':
            action.variant === 'primary',
          'liquid-glass border border-sunset-secondary/40 text-sunset-accent hover:border-sunset-secondary/70 hover:bg-sunset-primary/15':
            action.variant === 'secondary',
          'liquid-glass border border-sunset-primary/25 text-sunset-secondary/90 hover:text-sunset-accent':
            action.variant === 'ghost',
          'border border-emerald-400/40 bg-emerald-500/10 text-emerald-200 cursor-default':
            action.variant === 'status',
          'opacity-50 cursor-not-allowed': action.disabled && action.variant !== 'status',
        }"
        @click="!action.disabled && action.onClick()"
      >
        {{ action.label }}
      </button>
    </div>
  </section>
</template>

<style scoped>
@keyframes pulse-slow {
  0%,
  100% {
    opacity: 0.5;
    transform: translate(-50%, -50%) scale(1);
  }
  50% {
    opacity: 0.85;
    transform: translate(-50%, -50%) scale(1.08);
  }
}
.animate-pulse-slow {
  animation: pulse-slow 6s ease-in-out infinite;
}
</style>
