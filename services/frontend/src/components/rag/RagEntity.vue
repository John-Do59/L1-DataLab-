<script setup lang="ts">
import { computed } from 'vue'
import { tokens } from '../../theme/tokens'
import OracleGalaxy from './OracleGalaxy.vue'

export type RagEntityState = 'idle' | 'listening' | 'generating' | 'responding'
export type EntityMood = 'stable' | 'risky' | 'uncertain' | 'glitch'

const props = withDefaults(
  defineProps<{
    state: RagEntityState
    mood?: EntityMood
    streamIntensity?: number
    /** Même taille que RAG par défaut ; ex. `280px` pour la vue prédiction */
    haloSize?: string
    showStatus?: boolean
  }>(),
  { mood: 'stable', streamIntensity: 0, showStatus: true }
)

const stateLabels: Record<RagEntityState, string> = {
  idle: 'Mode repos — oracle en veille',
  listening: 'Écoute active — signal entrant',
  generating: 'Synthèse neuronale en cours',
  responding: 'Diffusion de la réponse',
}

const moodLabels: Record<EntityMood, string> = {
  stable: 'Signal stable — haute confiance',
  risky: 'Match à risque — variance élevée',
  uncertain: 'Incertitude tactique modérée',
  glitch: 'Données partielles — recalibrage',
}

const statusText = computed(() => {
  if (props.state === 'generating') return moodLabels[props.mood]
  return stateLabels[props.state]
})

const moodPalette = computed(() => tokens.oracle.moods[props.mood])

const shellStyle = computed(() => {
  const m = moodPalette.value
  const intensity = Math.min(1, Math.max(0, props.streamIntensity))
  return {
    '--vortex-primary': m.primary,
    '--vortex-secondary': m.secondary,
    '--vortex-glow': m.glow,
    '--vortex-brand': tokens.colors.brand.primary,
    '--vortex-accent': tokens.colors.brand.accent,
    '--stream-intensity': String(intensity),
  } as Record<string, string>
})

const haloIntensity = computed(() => {
  const base =
    tokens.oracle.glowIntensity[
      props.state === 'idle'
        ? 'idle'
        : props.state === 'listening'
          ? 'listening'
          : props.state === 'generating'
            ? 'generating'
            : 'responding'
    ]
  return Math.min(1, base + props.streamIntensity * 0.5)
})
</script>

<template>
  <div
    class="rag-entity-shell"
    :class="[
      `rag-entity-shell--${state}`,
      `rag-entity-shell--mood-${mood}`,
    ]"
    :style="shellStyle"
    role="img"
    :aria-label="statusText"
  >
    <div class="rag-entity-aura rag-entity-aura--primary" aria-hidden="true" />
    <div class="rag-entity-aura rag-entity-aura--secondary" aria-hidden="true" />

    <OracleGalaxy :intensity="haloIntensity" :size="haloSize" />

    <div v-if="showStatus" class="rag-entity-status">
      <span class="rag-entity-status-dot" />
      <span class="rag-entity-status-text">{{ statusText }}</span>
    </div>
  </div>
</template>

<style scoped>
.rag-entity-shell {
  position: relative;
  width: 100%;
  max-width: 420px;
  margin: 0 auto;
  padding: 0.5rem 0;
  transition: filter 0.6s ease;
}

.rag-entity-aura {
  position: absolute;
  left: 50%;
  top: 42%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  pointer-events: none;
  filter: blur(56px);
  z-index: 0;
}

.rag-entity-aura--primary {
  width: 85%;
  height: 70%;
  background: var(--vortex-glow);
  opacity: 0.45;
}

.rag-entity-aura--secondary {
  width: 60%;
  height: 50%;
  background: color-mix(in srgb, var(--vortex-accent) 25%, transparent);
  opacity: 0.35;
}

.oracle-halo {
  position: relative;
  z-index: 1;
}

.rag-entity-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: rgba(246, 179, 229, 0.7);
  position: relative;
  z-index: 2;
}

.rag-entity-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--vortex-accent);
  box-shadow: 0 0 8px var(--vortex-primary);
}

/* --- idle --- */
.rag-entity-shell--idle .rag-entity-status-dot {
  animation: rag-pulse-soft 3s ease-in-out infinite;
}

/* --- listening --- */
.rag-entity-shell--listening .oracle-halo :deep(.oracle-halo__rays) {
  animation-duration: 18s;
}

.rag-entity-shell--listening .oracle-halo :deep(.oracle-halo__img) {
  filter: drop-shadow(0 0 40px var(--vortex-glow)) saturate(1.08);
}

.rag-entity-shell--listening .rag-entity-status-dot {
  animation: rag-pulse-fast 0.8s ease-in-out infinite;
}

/* --- generating --- */
.rag-entity-shell--generating .oracle-halo :deep(.oracle-halo__rays) {
  animation-duration: calc(14s - 8s * var(--stream-intensity, 0));
}

.rag-entity-shell--generating .oracle-halo :deep(.oracle-halo__ring-border) {
  animation-duration: calc(12s - 6s * var(--stream-intensity, 0));
}

.rag-entity-shell--generating .oracle-halo :deep(.oracle-halo__img) {
  filter: drop-shadow(
      0 0 calc(36px + 50px * var(--stream-intensity, 0)) var(--vortex-glow)
    )
    saturate(calc(1.1 + 0.15 * var(--stream-intensity, 0)));
}

.rag-entity-shell--generating .rag-entity-aura--primary {
  opacity: calc(0.5 + 0.4 * var(--stream-intensity, 0));
}

/* --- responding --- */
.rag-entity-shell--responding .oracle-halo :deep(.oracle-halo__radiance) {
  opacity: 0.95;
}

.rag-entity-shell--responding .oracle-halo :deep(.oracle-halo__img) {
  filter: drop-shadow(0 0 56px var(--vortex-glow)) saturate(1.15);
}

/* --- moods (idle / listening — ne pas écraser generating) --- */
.rag-entity-shell--mood-stable:not(.rag-entity-shell--generating):not(.rag-entity-shell--responding)
  .oracle-halo
  :deep(.oracle-halo__img) {
  filter: drop-shadow(0 0 32px rgba(34, 211, 238, 0.45)) saturate(1.05);
}

.rag-entity-shell--mood-risky:not(.rag-entity-shell--generating):not(.rag-entity-shell--responding)
  .oracle-halo
  :deep(.oracle-halo__img) {
  filter: drop-shadow(0 0 36px rgba(249, 115, 22, 0.5)) saturate(1.15) hue-rotate(-8deg);
}

.rag-entity-shell--mood-uncertain:not(.rag-entity-shell--generating):not(.rag-entity-shell--responding)
  .oracle-halo
  :deep(.oracle-halo__img) {
  filter: drop-shadow(0 0 34px rgba(168, 85, 247, 0.45)) saturate(1.08);
}

.rag-entity-shell--mood-glitch .oracle-halo :deep(.oracle-halo__rays) {
  animation-duration: 8s;
  opacity: 0.55;
}

@keyframes rag-pulse-soft {
  0%,
  100% {
    opacity: 0.5;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.3);
  }
}

@keyframes rag-pulse-fast {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.4;
    transform: scale(0.85);
  }
}

</style>
