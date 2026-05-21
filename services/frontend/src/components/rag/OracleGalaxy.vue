<script setup lang="ts">
import { computed } from 'vue'
import haloImg from '../../assets/rag/oracle-halo.png'

const props = withDefaults(
  defineProps<{
    intensity?: number
    /** Taille du conteneur carré (ex. `280px`, `min(340px, 88vw)`) */
    size?: string
  }>(),
  { size: 'min(340px, 88vw)' }
)

const haloStyle = computed(() => ({
  '--halo-intensity': String(props.intensity ?? 0),
  '--halo-size': props.size,
}))
</script>

<template>
  <div class="oracle-halo" :style="haloStyle" aria-hidden="true">
    <div class="oracle-halo__radiance" />
    <div class="oracle-halo__rays" />
    <div class="oracle-halo__ring-glow" />
    <div class="oracle-halo__ring-border" />
    <img
      :src="haloImg"
      alt=""
      class="oracle-halo__img"
      draggable="false"
    />
  </div>
</template>

<style scoped>
.oracle-halo {
  position: relative;
  width: var(--halo-size, min(340px, 88vw));
  aspect-ratio: 1;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
}

/* Rayonnement radial autour du cercle */
.oracle-halo__radiance {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 100%;
  height: 100%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  background: radial-gradient(
    circle at 50% 50%,
    transparent 30%,
    color-mix(in srgb, var(--vortex-glow, rgba(200, 118, 255, 0.4)) 25%, transparent) 36%,
    color-mix(in srgb, var(--vortex-brand, #7232f2) 18%, transparent) 42%,
    color-mix(in srgb, var(--vortex-accent, #f6b3e5) 10%, transparent) 48%,
    transparent 58%
  );
  opacity: calc(0.55 + 0.35 * var(--halo-intensity, 0));
}

/* Faisceaux circulaires — rotation lente, pas de clignotement */
.oracle-halo__rays {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 88%;
  height: 88%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  background: repeating-conic-gradient(
    from 0deg at 50% 50%,
    transparent 0deg 7deg,
    color-mix(in srgb, var(--vortex-accent, #f6b3e5) 14%, transparent) 7deg 8deg,
    transparent 8deg 15deg
  );
  mask: radial-gradient(
    circle,
    transparent 34%,
    #000 36%,
    #000 50%,
    transparent 54%
  );
  -webkit-mask: radial-gradient(
    circle,
    transparent 34%,
    #000 36%,
    #000 50%,
    transparent 54%
  );
  opacity: calc(0.35 + 0.25 * var(--halo-intensity, 0));
  animation: halo-rays-spin 28s linear infinite;
}

.oracle-halo__ring-glow,
.oracle-halo__ring-border {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 72%;
  height: 72%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  pointer-events: none;
}

.oracle-halo__ring-glow {
  z-index: 0;
  box-shadow:
    0 0 12px color-mix(in srgb, var(--vortex-accent, #f6b3e5) 45%, transparent),
    0 0 28px color-mix(in srgb, var(--vortex-glow, rgba(200, 118, 255, 0.4)) 100%, transparent),
    0 0 48px color-mix(in srgb, var(--vortex-brand, #7232f2) 40%, transparent),
    0 0 72px color-mix(in srgb, var(--vortex-primary, #c876ff) 20%, transparent);
  opacity: calc(0.5 + 0.35 * var(--halo-intensity, 0));
}

.oracle-halo__ring-border {
  z-index: 2;
  background: conic-gradient(
    from 0deg,
    color-mix(in srgb, var(--vortex-primary, #22d3ee) 65%, transparent),
    color-mix(in srgb, var(--vortex-accent, #f6b3e5) 75%, transparent),
    color-mix(in srgb, var(--vortex-brand, #7232f2) 70%, transparent),
    color-mix(in srgb, var(--vortex-secondary, #7c3aed) 65%, transparent),
    color-mix(in srgb, var(--vortex-primary, #22d3ee) 65%, transparent)
  );
  mask: radial-gradient(
    circle,
    transparent calc(50% - 1px),
    #000 calc(50% - 0.5px),
    #000 calc(50% + 0.5px),
    transparent calc(50% + 1px)
  );
  -webkit-mask: radial-gradient(
    circle,
    transparent calc(50% - 1px),
    #000 calc(50% - 0.5px),
    #000 calc(50% + 0.5px),
    transparent calc(50% + 1px)
  );
  filter: drop-shadow(0 0 6px color-mix(in srgb, var(--vortex-accent, #f6b3e5) 60%, transparent));
  opacity: calc(0.7 + 0.25 * var(--halo-intensity, 0));
  animation: halo-ring-spin 20s linear infinite;
}

.oracle-halo__img {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center;
  user-select: none;
  pointer-events: none;
  filter: drop-shadow(
    0 0 calc(24px + 32px * var(--halo-intensity, 0))
      color-mix(in srgb, var(--vortex-glow, rgba(200, 118, 255, 0.5)) 100%, transparent)
  );
}

@keyframes halo-rays-spin {
  from {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  to {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}

@keyframes halo-ring-spin {
  from {
    transform: translate(-50%, -50%) rotate(0deg);
  }
  to {
    transform: translate(-50%, -50%) rotate(360deg);
  }
}
</style>
