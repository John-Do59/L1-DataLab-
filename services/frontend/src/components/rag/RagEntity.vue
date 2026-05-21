<script setup lang="ts">
import { computed } from 'vue'
import entityImg from '../../assets/backgrounds/ballon-entite.png'

export type RagEntityState = 'idle' | 'listening' | 'generating' | 'responding'
export type EntityMood = 'stable' | 'risky' | 'uncertain' | 'glitch'

const props = withDefaults(
  defineProps<{
    state: RagEntityState
    mood?: EntityMood
    streamIntensity?: number
  }>(),
  { mood: 'stable', streamIntensity: 0 }
)

const stateLabels: Record<RagEntityState, string> = {
  idle: 'Mode repos — entité en veille',
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

const glowStyle = computed(() => ({
  '--stream-intensity': String(Math.min(1, Math.max(0, props.streamIntensity))),
}))
</script>

<template>
  <div
    class="rag-entity-shell"
    :class="[
      `rag-entity-shell--${state}`,
      `rag-entity-shell--mood-${mood}`,
    ]"
    :style="glowStyle"
    role="img"
    :aria-label="statusText"
  >
    <!-- Border glow overlay -->
    <div class="rag-entity-border-glow" aria-hidden="true" />
    <div class="rag-entity-border-scan" aria-hidden="true" />

    <!-- Orbital rings (generating / responding) -->
    <div class="rag-entity-orbit rag-entity-orbit--1" aria-hidden="true" />
    <div class="rag-entity-orbit rag-entity-orbit--2" aria-hidden="true" />

    <!-- Ambient cores -->
    <div class="rag-entity-aura rag-entity-aura--primary" aria-hidden="true" />
    <div class="rag-entity-aura rag-entity-aura--secondary" aria-hidden="true" />

    <div class="rag-entity-frame liquid-glass-strong">
      <img
        :src="entityImg"
        alt="Entité IA L1 DataLab"
        class="rag-entity-image"
      />
      <div class="rag-entity-shimmer" aria-hidden="true" />
    </div>

    <div class="rag-entity-status">
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
  padding: 1.5rem;
  transition: filter 0.6s ease;
}

.rag-entity-frame {
  position: relative;
  z-index: 2;
  border-radius: 2rem;
  padding: 1.25rem;
  overflow: hidden;
  transition: transform 0.5s ease, box-shadow 0.5s ease;
}

.rag-entity-image {
  width: 100%;
  height: auto;
  max-height: 220px;
  object-fit: contain;
  object-position: center;
  display: block;
  margin: 0 auto;
  filter: drop-shadow(0 0 24px rgba(200, 118, 255, 0.35));
  transition: transform 0.6s ease, filter 0.6s ease;
}

.rag-entity-shimmer {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    105deg,
    transparent 40%,
    rgba(246, 179, 229, 0.12) 50%,
    transparent 60%
  );
  transform: translateX(-100%);
  pointer-events: none;
}

.rag-entity-border-glow {
  position: absolute;
  inset: 0.5rem;
  border-radius: 2.25rem;
  border: 1px solid rgba(200, 118, 255, 0.25);
  pointer-events: none;
  z-index: 1;
  transition: box-shadow 0.4s ease, border-color 0.4s ease;
}

.rag-entity-border-scan {
  position: absolute;
  inset: 0.25rem;
  border-radius: 2.5rem;
  opacity: 0;
  pointer-events: none;
  z-index: 0;
  background: conic-gradient(
    from 0deg,
    transparent,
    rgba(114, 50, 242, 0.5),
    rgba(246, 179, 229, 0.6),
    transparent
  );
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  padding: 2px;
}

.rag-entity-orbit {
  position: absolute;
  left: 50%;
  top: 50%;
  border-radius: 50%;
  border: 1px dashed rgba(200, 118, 255, 0.2);
  pointer-events: none;
  opacity: 0;
  transform: translate(-50%, -50%);
}

.rag-entity-orbit--1 {
  width: 115%;
  height: 115%;
}

.rag-entity-orbit--2 {
  width: 130%;
  height: 130%;
  border-style: dotted;
}

.rag-entity-aura {
  position: absolute;
  left: 50%;
  top: 45%;
  transform: translate(-50%, -50%);
  border-radius: 50%;
  pointer-events: none;
  filter: blur(40px);
}

.rag-entity-aura--primary {
  width: 70%;
  height: 55%;
  background: rgba(114, 50, 242, 0.35);
}

.rag-entity-aura--secondary {
  width: 50%;
  height: 40%;
  background: rgba(246, 179, 229, 0.2);
}

.rag-entity-status {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1rem;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: rgba(246, 179, 229, 0.7);
  position: relative;
  z-index: 3;
}

.rag-entity-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #c876ff;
  box-shadow: 0 0 8px #c876ff;
}

/* --- idle / repos --- */
.rag-entity-shell--idle .rag-entity-image {
  animation: rag-breathe 4s ease-in-out infinite;
}

.rag-entity-shell--idle .rag-entity-status-dot {
  animation: rag-pulse-soft 3s ease-in-out infinite;
}

.rag-entity-shell--idle .rag-entity-aura--primary {
  animation: rag-aura-idle 5s ease-in-out infinite;
}

/* --- listening --- */
.rag-entity-shell--listening .rag-entity-image {
  animation: rag-listen 1.2s ease-in-out infinite;
  filter: drop-shadow(0 0 32px rgba(200, 118, 255, 0.55));
}

.rag-entity-shell--listening .rag-entity-border-glow {
  border-color: rgba(246, 179, 229, 0.5);
  box-shadow: 0 0 35px rgba(200, 118, 255, 0.35);
}

.rag-entity-shell--listening .rag-entity-status-dot {
  background: #f6b3e5;
  animation: rag-pulse-fast 0.8s ease-in-out infinite;
}

/* --- generating --- */
.rag-entity-shell--generating .rag-entity-frame {
  animation: rag-frame-pulse 1.5s ease-in-out infinite;
}

.rag-entity-shell--generating .rag-entity-image {
  animation: rag-generate 0.9s ease-in-out infinite;
  filter: drop-shadow(0 0 40px rgba(114, 50, 242, 0.7));
}

.rag-entity-shell--generating .rag-entity-border-glow {
  border-color: rgba(114, 50, 242, 0.7);
  box-shadow:
    0 0 calc(20px + 40px * var(--stream-intensity, 0)) rgba(114, 50, 242, 0.5),
    0 0 calc(50px + 30px * var(--stream-intensity, 0)) rgba(200, 118, 255, 0.4),
    inset 0 0 30px rgba(114, 50, 242, 0.15);
  animation: rag-border-glow calc(1.4s - 0.6s * var(--stream-intensity, 0)) ease-in-out infinite;
}

/* --- moods (AI Football Oracle) --- */
.rag-entity-shell--mood-stable.rag-entity-shell--generating .rag-entity-border-glow,
.rag-entity-shell--mood-stable.rag-entity-shell--idle .rag-entity-border-glow {
  border-color: rgba(56, 189, 248, 0.55);
  box-shadow: 0 0 45px rgba(56, 189, 248, 0.35);
}
.rag-entity-shell--mood-stable .rag-entity-aura--primary {
  background: rgba(56, 189, 248, 0.35);
}

.rag-entity-shell--mood-risky .rag-entity-border-glow {
  border-color: rgba(251, 146, 60, 0.65);
  box-shadow: 0 0 40px rgba(239, 68, 68, 0.4);
}
.rag-entity-shell--mood-risky .rag-entity-aura--primary {
  background: rgba(239, 68, 68, 0.35);
}
.rag-entity-shell--mood-risky.rag-entity-shell--generating .rag-entity-image {
  animation: rag-generate-risk 0.7s ease-in-out infinite;
}

.rag-entity-shell--mood-uncertain .rag-entity-border-glow {
  border-color: rgba(251, 191, 36, 0.55);
  box-shadow: 0 0 35px rgba(245, 158, 11, 0.35);
}
.rag-entity-shell--mood-uncertain .rag-entity-aura--primary {
  background: rgba(245, 158, 11, 0.3);
}

.rag-entity-shell--mood-glitch .rag-entity-image {
  animation: rag-glitch 0.35s steps(2) infinite;
}
.rag-entity-shell--mood-glitch .rag-entity-border-glow {
  border-color: rgba(248, 113, 113, 0.5);
  animation: rag-glitch-border 0.25s steps(3) infinite;
}
.rag-entity-shell--mood-glitch .rag-entity-aura--primary {
  background: rgba(248, 113, 113, 0.25);
  animation: rag-aura-glitch 0.4s steps(2) infinite;
}

.rag-entity-shell--generating .rag-entity-border-scan {
  opacity: 1;
  animation: rag-spin 3s linear infinite;
}

.rag-entity-shell--generating .rag-entity-orbit {
  opacity: 1;
}

.rag-entity-shell--generating .rag-entity-orbit--1 {
  animation: rag-spin 8s linear infinite;
}

.rag-entity-shell--generating .rag-entity-orbit--2 {
  animation: rag-spin-reverse 12s linear infinite;
}

.rag-entity-shell--generating .rag-entity-shimmer {
  animation: rag-shimmer 1.8s ease-in-out infinite;
}

.rag-entity-shell--generating .rag-entity-aura--primary {
  animation: rag-aura-active 1s ease-in-out infinite;
}

/* --- responding --- */
.rag-entity-shell--responding .rag-entity-image {
  animation: rag-respond 0.6s ease-out 2;
  filter: drop-shadow(0 0 48px rgba(246, 179, 229, 0.8));
}

.rag-entity-shell--responding .rag-entity-border-glow {
  border-color: rgba(246, 179, 229, 0.8);
  box-shadow: 0 0 60px rgba(246, 179, 229, 0.5);
  animation: rag-flash 0.6s ease-out 2;
}

@keyframes rag-breathe {
  0%, 100% { transform: scale(1) translateY(0); }
  50% { transform: scale(1.03) translateY(-6px); }
}

@keyframes rag-listen {
  0%, 100% { transform: scale(1) rotate(0deg); }
  25% { transform: scale(1.04) rotate(-1deg); }
  75% { transform: scale(1.04) rotate(1deg); }
}

@keyframes rag-generate {
  0%, 100% { transform: scale(1.02) translateY(-2px); }
  50% { transform: scale(1.06) translateY(-8px); }
}

@keyframes rag-respond {
  0% { transform: scale(1.08); }
  50% { transform: scale(1.02); }
  100% { transform: scale(1); }
}

@keyframes rag-frame-pulse {
  0%, 100% { box-shadow: 0 8px 40px rgba(32, 17, 91, 0.4); }
  50% { box-shadow: 0 8px 60px rgba(114, 50, 242, 0.5); }
}

@keyframes rag-border-glow {
  0%, 100% {
    box-shadow:
      0 0 20px rgba(114, 50, 242, 0.4),
      0 0 40px rgba(200, 118, 255, 0.25);
  }
  50% {
    box-shadow:
      0 0 35px rgba(114, 50, 242, 0.7),
      0 0 70px rgba(246, 179, 229, 0.45);
  }
}

@keyframes rag-spin {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes rag-spin-reverse {
  from { transform: translate(-50%, -50%) rotate(360deg); }
  to { transform: translate(-50%, -50%) rotate(0deg); }
}

@keyframes rag-shimmer {
  0% { transform: translateX(-100%); opacity: 0; }
  40% { opacity: 1; }
  100% { transform: translateX(100%); opacity: 0; }
}

@keyframes rag-pulse-soft {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.3); }
}

@keyframes rag-pulse-fast {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

@keyframes rag-aura-idle {
  0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.75; transform: translate(-50%, -50%) scale(1.08); }
}

@keyframes rag-aura-active {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

@keyframes rag-flash {
  0% { opacity: 1; }
  100% { opacity: 0.6; }
}

@keyframes rag-generate-risk {
  0%, 100% { transform: scale(1.03) translateX(0); }
  50% { transform: scale(1.06) translateX(3px); }
}

@keyframes rag-glitch {
  0% { transform: translate(0); filter: hue-rotate(0deg); }
  33% { transform: translate(-2px, 1px); filter: hue-rotate(15deg); }
  66% { transform: translate(2px, -1px); filter: hue-rotate(-10deg); }
  100% { transform: translate(0); }
}

@keyframes rag-glitch-border {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

@keyframes rag-aura-glitch {
  0%, 100% { opacity: 0.4; }
  50% { opacity: 0.9; }
}
</style>
