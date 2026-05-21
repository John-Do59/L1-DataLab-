<script setup lang="ts">
import { computed } from 'vue'
import { getTeamVisuals } from '../../utils/teamVisuals'

const props = withDefaults(
  defineProps<{
    teamName: string
    size?: 'sm' | 'md' | 'lg'
    ring?: boolean
  }>(),
  { size: 'md', ring: true },
)

const visuals = computed(() => getTeamVisuals(props.teamName))

const sizeClass = computed(() => {
  if (props.size === 'sm') return 'w-10 h-10'
  if (props.size === 'lg') return 'w-16 h-16'
  return 'w-14 h-14'
})
</script>

<template>
  <div
    class="team-glow flex items-center justify-center rounded-full transition-all duration-500"
    :class="[sizeClass, ring ? 'border' : '']"
    :style="{
      ...(visuals?.cssVars ?? {}),
      '--tv-glow-filter': visuals?.glowFilter,
      borderColor: visuals ? 'var(--tv-border)' : 'rgba(255,255,255,0.1)',
      boxShadow: visuals ? '0 0 24px var(--tv-glow)' : undefined,
      background: visuals ? 'var(--tv-surface)' : 'rgba(0,0,0,0.4)',
    }"
  >
    <slot />
  </div>
</template>

<style scoped>
.team-glow :deep(img) {
  filter: var(--tv-glow-filter, drop-shadow(0 0 8px var(--tv-glow)));
}
</style>
